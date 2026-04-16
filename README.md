# 🛡️ CloudShield AI — Cloud Security Policy Chatbot

A RAG-powered chatbot that answers questions about your organization's cloud security policies using **LangChain**, **ChromaDB**, and **OpenAI GPT-4o-mini** — served through a beautiful **Streamlit** UI.

---

## ✨ Features

- **PDF ingestion pipeline** — drop any PDF into `data/policies/` and index it
- **300-word overlapping chunks** with RecursiveCharacterTextSplitter
- **OpenAI embeddings** (`text-embedding-3-small`) stored locally in ChromaDB
- **Grounded answers** — the LLM is instructed to answer ONLY from retrieved context
- **Source citations** — every answer shows the source document + page number
- **Streamlit dark-mode UI** with chat history, suggested questions, and PDF upload
- **3 sample policy PDFs** auto-generated (NIST CSF, AWS Security, SOC 2)

---

## 🚀 Quick Start

### 1. Prerequisites

- Python 3.10 or higher
- An **OpenAI API key** ([get one here](https://platform.openai.com/api-keys))

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Set your API key

```bash
# Copy the template
copy .env.example .env

# Open .env and replace the placeholder with your real API key
# OPENAI_API_KEY=sk-your-real-key-here
```

### 4. Generate sample PDFs (optional but recommended for demo)

```bash
python create_sample_pdfs.py
```

This creates 3 realistic policy PDFs in `data/policies/`:
- `sample_nist_csf.pdf` — NIST Cybersecurity Framework
- `sample_aws_security.pdf` — AWS Security Best Practices
- `sample_soc2_overview.pdf` — SOC 2 Type II Overview

### 5. Index the documents

```bash
python ingest.py
```

Output example:
```
📂 Found 3 PDF file(s):
   Loading: sample_aws_security.pdf ... ✅ (8 pages)
   Loading: sample_nist_csf.pdf ... ✅ (6 pages)
   Loading: sample_soc2_overview.pdf ... ✅ (5 pages)
✂️  Chunked into 87 segments
   Batch 1/1 (87 chunks) ... ✅
═══════════════════════════════════════════════════════
  ✅  INGESTION COMPLETE
  📄  Files indexed  : 3
  📃  Total pages    : 19
  🧩  Total chunks   : 87
  ⏱️   Time elapsed   : 12.4s
═══════════════════════════════════════════════════════
```

### 6. Launch the chatbot

```bash
streamlit run app.py
```

Open your browser at **http://localhost:8501** 🎉

---

## 📁 Project Structure

```
mini/
├── app.py                    # Streamlit chat UI
├── ingest.py                 # PDF ingestion + embedding pipeline
├── rag_chain.py              # RAG retrieval + LLM answer generation
├── config.py                 # Centralized configuration
├── create_sample_pdfs.py     # Generates demo policy PDFs
├── requirements.txt          # Python dependencies
├── .env.example              # API key template
├── .env                      # Your API keys (do NOT commit!)
└── data/
    ├── policies/             # 📂 Drop your PDFs here
    │   ├── sample_nist_csf.pdf
    │   ├── sample_aws_security.pdf
    │   └── sample_soc2_overview.pdf
    └── chroma_db/            # ChromaDB vector store (auto-created)
```

---

## 💬 Example Questions

| Question | Expected Source |
|---|---|
| What MFA requirements apply to cloud console access? | NIST CSF / AWS Security |
| How should API keys and secrets be stored on AWS? | AWS Security Best Practices |
| What are our RTO and RPO targets for Tier 1 systems? | NIST CSF |
| What does SOC 2 CC6.1 require for access control? | SOC 2 Overview |
| What is the patch SLA for Critical vulnerabilities? | NIST CSF |
| How must S3 buckets be secured? | AWS Security Best Practices |

---

## 📤 Using Your Own PDFs

1. Copy your PDF files into `data/policies/`
2. Run `python ingest.py --reset` to re-index everything
3. Or upload directly via the **sidebar** in the Streamlit UI and click **▶ Index**

---

## ⚙️ Configuration

Edit `config.py` to change:

| Setting | Default | Description |
|---|---|---|
| `CHUNK_SIZE` | `1200` chars (~300 words) | Size of each text chunk |
| `CHUNK_OVERLAP` | `200` chars (~50 words) | Overlap between chunks |
| `TOP_K` | `5` | Chunks retrieved per query |
| `LLM_MODEL` | `gpt-4o-mini` | OpenAI chat model |
| `EMBEDDING_MODEL` | `text-embedding-3-small` | OpenAI embedding model |
| `LLM_TEMPERATURE` | `0.0` | 0 = most factual |

---

## 🔒 Security Notes

- **Never commit `.env`** — add it to `.gitignore`
- ChromaDB data is stored **locally** in `data/chroma_db/` — no cloud upload
- The LLM is instructed to answer only from context, reducing hallucination risk

---

## 🛠️ Re-indexing

```bash
# Add new PDFs without losing existing index
python ingest.py

# Wipe everything and re-index from scratch
python ingest.py --reset
```
