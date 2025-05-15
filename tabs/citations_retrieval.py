import os
import streamlit as st
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from groq import Groq
from langchain.schema import Document


# === CONFIGURATION ===
# Paths and model settings
DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "RAGdata.txt")
CHROMA_DIR = "./chroma_store"
EMBEDDING_MODEL = "text-embedding-3-small"

# System prompt defining the assistant's behavior and scope
SYSTEM_PROMPT = """You are an expert in Pakistani legal research. You ONLY provide relevant statutes, case law citations, and brief summaries based on user queries strictly related to **Pakistani family law**.

### If a query is unrelated to Pakistani family law (e.g., criminal law, international law, general legal advice), politely refuse to answer and remind the user of your domain restriction.
### Focus areas include: divorce, child custody, maintenance (nafaqah), polygamy, nikah, dissolution of marriage, guardianship, inheritance under family law, and related topics."""


@st.cache_resource
def load_retriever():
    """
    Load a Chroma retriever for semantic search over legal documents.

    If a Chroma index already exists at the specified directory, it is loaded directly
    to avoid redundant computation. Otherwise, the raw text file is loaded, split into
    chunks, embedded using OpenAI embeddings, and a new Chroma index is created and persisted.

    The result is cached using Streamlit's `@st.cache_resource` to improve performance
    by ensuring the retriever is loaded or built only once per session.
    """
    
    # Retrieve OpenAI embedding API key
    openai_key = st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")

    # Initialize the embedding model
    embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL, openai_api_key=openai_key)

    # Check if a Chroma index already exists; if so, load and return retriever
    if os.path.exists(os.path.join(CHROMA_DIR, "index")):
        return Chroma(
            persist_directory=CHROMA_DIR,
            embedding_function=embeddings
        ).as_retriever(search_kwargs={"k": 3})

    # Otherwise, load raw text data from file and process it
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        raw_text = f.read()

    # Wrap the text as a single document object for splitting
    docs = [Document(page_content=raw_text)]

    # Split the document into smaller overlapping chunks for better semantic matching
    splitter = RecursiveCharacterTextSplitter(chunk_size=100, chunk_overlap=20)
    chunks = splitter.split_documents(docs)

    # Create a new Chroma index from the chunks and persist it to disk
    vectordb = Chroma.from_documents(chunks, embeddings, persist_directory=CHROMA_DIR)
    
    # Return retriever interface
    return vectordb.as_retriever(search_kwargs={"k": 3})


def get_context_from_docs(query: str) -> str:
    """
    Retrieve the top-k most relevant document chunks based on the user's query.

    This function uses the cached retriever to fetch semantically similar
    chunks from the legal knowledge base. If an error occurs, it is caught
    and displayed in the Streamlit UI for debugging.
    """
    try:
        retriever = load_retriever()  # Load cached or pre-built retriever
        retrieved_docs = retriever.get_relevant_documents(query)  # Perform similarity search
        return "\n\n".join([doc.page_content for doc in retrieved_docs])  # Combine results
    except Exception as e:
        st.error("❌ Failed to retrieve context from documents.")
        st.exception(e)
        return f"Error: {e}"



def format_full_prompt(prompt: str, context: str) -> str:
    """
    Generate the full prompt sent to the model, including structure and context.
    """
    return f"""
{SYSTEM_PROMPT}

You must follow this format strictly:

1. **Summary**: A concise 1-2 sentence summary relevant to the query.
2. **Relevant Statutes**: List 1-2 relevant Pakistani laws with section numbers.
3. **Case Law**: List 3 relevant Pakistani cases, including case name and citation (e.g., PLD 1985 SC 30), each followed by a 1-sentence summary.
4. **Key Points**: Bullet points (3-4) highlighting essential guidance for the user's legal query.

Context (if any):
{context}

Question:
{prompt}
"""


def stream_response(prompt: str, context: str, client) -> str:
    """
    Calls the Groq API with the full prompt and streams the response back to the user.
    """
    full_prompt = format_full_prompt(prompt, context)
    response_container = st.empty()
    full_response = ""

    stream = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": full_prompt}
        ],
        temperature=0.4,
        max_tokens=1024,
        top_p=0.9,
        stream=True,
    )

    # Stream each chunk and append it to the response
    for chunk in stream:
        content = chunk.choices[0].delta.content or ""
        full_response += content
        response_container.markdown(full_response, unsafe_allow_html=True)

    return full_response


def render(client):
    """
    Renders the Streamlit UI for the Citations Retrieval tab.
    Handles user input, document retrieval, prompt construction, and displaying the model's response.
    """
    tab_name = "Citations Retrieval"

    # Initialize session message history for this tab
    if tab_name not in st.session_state.messages:
        st.session_state.messages[tab_name] = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]

    # Title of the tab
    st.header("📚 Citations Retrieval || قانونی حوالہ جات")

    # Display chat history
    for msg in st.session_state.messages[tab_name]:
        if msg["role"] != "system":
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    # Chat input for new user query
    if prompt := st.chat_input("Enter a legal topic to get relevant citations…"):
        # Clear previous history and add new user prompt
        st.session_state.messages[tab_name] = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ]

        # Retrieve relevant context from vector DB
        context = get_context_from_docs(prompt)

        # If context is insufficient, rely only on model
        if "Error" in context or len(context.strip()) < 100:
            context_note = "**Note:** Context was insufficient, relying on model knowledge.\n"
            context = ""
        else:
            context_note = ""

        # Display streaming response
        with st.chat_message("assistant"):
            groq_client = Groq(api_key=st.secrets["GROQ_KEY"])
            response = stream_response(prompt, context, groq_client)

        # Save assistant response in session
        st.session_state.messages[tab_name].append({
            "role": "assistant",
            "content": context_note + response
        })
