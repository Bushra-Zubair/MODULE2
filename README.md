# 🧑‍⚖️ Wakeel | وکیل

A Streamlit-based multilingual legal assistant for Pakistani Family Law, offering legal consulting, automated petition drafting, and citation retrieval—powered by OpenAI and Groq APIs.

---

## 📌 Project Overview

**Wakeel** is a browser-based legal help desk application for users seeking guidance under Pakistani **family law**. It provides three key services:

1. **Legal Consulting**: Ask questions in English or Urdu and get AI-generated responses tailored to both legal professionals and the general public.
2. **Petition Drafting**: Auto-generate formal legal petitions (e.g., Khula, Custody, Maintenance) based on user input.
3. **Citations Retrieval**: Get summaries of Pakistani case law, statutes, and legal commentary relevant to a specific family law query using RAG (Retrieval-Augmented Generation).

---

## 🗂️ Project Structure

```
wakeel/
│
├── main.py                        # Entry point, handles routing and layout
├── requirements.txt               # Dependencies
├── tabs/
│   ├── __init__.py                # Imports tab modules
│   ├── legal_consulting.py        # Chat interface using finetuned OpenAI model ("ft:gpt-4o-2024-08-06:iml-research:wakeel:BW4oryHJ")
│   ├── petition_drafting.py       # Petition drafting with Groq LLM (llama3-70b-8192)
│   └── citations_retrieval.py     # RAG pipeline using OpenAI Embeddings,Chroma DB, and Groq LLM (llama3-70b-8192)
├── data/
│   └── RAGdata.txt                # Source data used in citation retrieval
└── .streamlit/
    └── secrets.toml               # API keys (ignored by Git)
```

---

## ⚙️ Setup Instructions

### 1. Clone the Repo

```bash
git clone https://github.com/yourusername/wakeel.git
cd wakeel
```

### 2. Install Dependencies

It's recommended to use a virtual environment:

```bash
pip install -r requirements.txt
```

### 3. Set Secrets

Create a `.streamlit/secrets.toml` file (excluded from Git) with the following format:

```toml
OPENAI_API_KEY = "sk-..."
GROQ_KEY = "gsk-..."
```

### 4. Run the App

```bash
streamlit run main.py
```

---

## 💬 Features

### ✅ Legal Consulting Tab

* Uses a fine-tuned OpenAI model (`ft:gpt-4o-...`)
* Explains answers in both English and Urdu
* Covers topics like maintenance, child custody, nikah, polygamy, inheritance, etc.

### ✅ Petition Drafting Tab

* Choose between **Khula**, **Child Custody**, or **Maintenance** petitions
* Dynamically generated input forms
* Generates formatted legal petitions via Groq API
* Allows downloading as `.txt`

### ✅ Citations Retrieval Tab

* Performs semantic search over law corpus using OpenAI embeddings
* Fetches relevant cases, statutes, summaries
* Response format includes Summary, Laws, Case Law, Key Points
* Refuses queries outside Pakistani family law domain

---

## 🔐 Security

Sensitive credentials (API keys) are stored in `.streamlit/secrets.toml` and **not committed to Git**.

---

## 📚 Tech Stack

* [Streamlit](https://streamlit.io/)
* [OpenAI API](https://platform.openai.com/)
* [Groq API](https://console.groq.com/)
* [LangChain](https://www.langchain.com/)
* [ChromaDB](https://www.trychroma.com/)
* [Langchain Community Tools](https://python.langchain.com/)

---

## 🧪 Example Use Cases

* A user can ask: *"میرے شوہر نے 6 ماہ سے خرچہ نہیں دیا، میں کیا کر سکتی ہوں؟"*
  → Legal advice in Urdu and English

* A paralegal needs to draft a **Khula** petition
  → Fill form → Generate → Download

* A student wants case law on *“custody after divorce”*
  → Citation tab provides PLD, SCMR, and summaries

---

## 🚧 Future Work

* Add voice-to-text input via Whisper
* Expand domain coverage to criminal and civil law

---

## 🤝 Contribution

If you'd like to contribute, please fork the repository and submit a pull request. Issues and suggestions welcome!

---

## 📝 License

MIT License
