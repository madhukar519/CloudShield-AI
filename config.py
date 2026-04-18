"""
config.py — Centralized configuration for the Cloud Security Policy Chatbot.
"""

from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────────────────
BASE_DIR        = Path(__file__).parent
DATA_DIR        = BASE_DIR / "data"
POLICIES_DIR    = DATA_DIR / "policies"
CHROMA_DIR      = DATA_DIR / "chroma_db"

# ── ChromaDB ───────────────────────────────────────────────────────────────────
CHROMA_COLLECTION = "cloud_security_policies"

# ── Chunking ───────────────────────────────────────────────────────────────────
# ~300 words × 4 chars/word ≈ 1200 chars; overlap ~50 words ≈ 200 chars
CHUNK_SIZE    = 1200
CHUNK_OVERLAP = 200

# ── Embeddings (FREE local model — no API key needed) ─────────────────────────
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L12-v2"

# ── LLM Configuration ─────────────────────────────────────────────────────────
# Options: "openai", "bedrock"
MODEL_PROVIDER  = "bedrock"

# OpenAI settings
LLM_MODEL       = "gpt-4o-mini"
LLM_TEMPERATURE = 0.0
LLM_MAX_TOKENS  = 1024

# Amazon Bedrock settings
# Suggested: anthropic.claude-3-haiku-20240307-v1:0 (fast/cheap)
#            anthropic.claude-3-sonnet-20240229-v1:0 (powerful)
BEDROCK_MODEL   = "anthropic.claude-3-haiku-20240307-v1:0"
BEDROCK_REGION  = "us-east-1"

# ── Retrieval ──────────────────────────────────────────────────────────────────
TOP_K = 5

# ── System Prompt ──────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are a Cloud Security Policy Assistant. Your job is to answer
questions about the organization's cloud security policies, compliance guides, and
runbooks based ONLY on the retrieved policy documents provided to you as context.

Rules:
1. Answer ONLY using information in the provided context. Do NOT hallucinate.
2. If the answer is not found in the context, say: "I couldn't find that in the
   loaded policy documents. Please check with your security team."
3. Always cite the source document and page number at the end of your answer.
4. Be clear, concise, and professional.
5. If the question involves a security control, state the specific requirement.

Context from policy documents:
{context}
"""
