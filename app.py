"""
app.py — Cloud Security Policy Chatbot (Streamlit UI)
Run: streamlit run app.py
"""

import os
import sys
import subprocess
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

from config import POLICIES_DIR, CHROMA_DIR
from rag_chain import get_vectorstore, get_collection_stats, build_rag_chain, format_sources

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="CloudShield AI — Security Policy Chatbot",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp {
    background: linear-gradient(135deg, #0a0e1a 0%, #0d1321 40%, #111827 100%);
    color: #e2e8f0;
}
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 1rem; padding-bottom: 1rem; }

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d1321 0%, #111827 100%);
    border-right: 1px solid rgba(99,179,237,0.15);
}

.hero-banner {
    background: linear-gradient(135deg, #1a2744 0%, #1e3a5f 50%, #0f2a4a 100%);
    border: 1px solid rgba(99,179,237,0.25);
    border-radius: 16px;
    padding: 1.5rem 2rem;
    margin-bottom: 1.5rem;
    display: flex; align-items: center; gap: 1rem;
    box-shadow: 0 8px 32px rgba(0,0,0,0.4), inset 0 1px 0 rgba(255,255,255,0.05);
}
.hero-icon  { font-size: 2.8rem; filter: drop-shadow(0 0 12px #63b3ed); }
.hero-title { font-size: 1.6rem; font-weight: 700; color: #e2e8f0; margin: 0; line-height: 1.2; }
.hero-sub   { font-size: 0.85rem; color: #94a3b8; margin: 0.2rem 0 0; }

.status-badge {
    display: inline-flex; align-items: center; gap: 0.4rem;
    padding: 0.3rem 0.8rem; border-radius: 20px;
    font-size: 0.75rem; font-weight: 600; letter-spacing: 0.03em;
}
.status-ready   { background: rgba(72,187,120,0.15); border: 1px solid rgba(72,187,120,0.4); color: #68d391; }
.status-warning { background: rgba(246,173,85,0.15);  border: 1px solid rgba(246,173,85,0.4);  color: #f6ad55; }

.chat-wrap { display: flex; flex-direction: column; gap: 0.6rem; }
.chat-row  { display: flex; gap: 0.8rem; animation: fadeIn 0.3s ease; }
.chat-row.user      { flex-direction: row-reverse; }
.chat-row.assistant { flex-direction: row; }
.avatar {
    width: 36px; height: 36px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 1rem; flex-shrink: 0;
}
.avatar.user { background: linear-gradient(135deg,#4299e1,#667eea); }
.avatar.bot  { background: linear-gradient(135deg,#1a2744,#2d3748); border:1px solid #63b3ed55; }
.bubble {
    max-width: 75%; padding: 0.85rem 1.1rem;
    border-radius: 12px; line-height: 1.6; font-size: 0.93rem;
}
.bubble.user      { background:rgba(99,179,237,0.1); border:1px solid rgba(99,179,237,0.2); color:#bee3f8; text-align:right; }
.bubble.assistant { background:rgba(26,39,68,0.7);   border:1px solid rgba(99,179,237,0.1); color:#e2e8f0; }

.source-card {
    background: rgba(15,42,74,0.5); border:1px solid rgba(99,179,237,0.2);
    border-radius:8px; padding:0.7rem 0.9rem; margin:0.3rem 0; font-size:0.82rem;
}
.source-file    { color:#63b3ed; font-weight:600; font-family:'JetBrains Mono',monospace; }
.source-page    { color:#94a3b8; font-size:0.74rem; }
.source-snippet { color:#cbd5e0; margin-top:0.35rem; line-height:1.5; }

.stat-card { background:rgba(26,39,68,0.5); border:1px solid rgba(99,179,237,0.15); border-radius:10px; padding:0.8rem; margin:0.3rem 0; text-align:center; }
.stat-num  { font-size:1.6rem; font-weight:700; color:#63b3ed; }
.stat-lbl  { font-size:0.7rem; color:#94a3b8; text-transform:uppercase; letter-spacing:0.05em; }

.stChatInput > div { background:rgba(26,39,68,0.6)!important; border:1px solid rgba(99,179,237,0.25)!important; border-radius:12px!important; }
.stChatInput textarea { color:#e2e8f0!important; }

.stButton > button {
    background:linear-gradient(135deg,#1e3a5f,#2d4a7a)!important;
    color:#63b3ed!important; border:1px solid rgba(99,179,237,0.3)!important;
    border-radius:8px!important; font-weight:500!important; transition:all 0.2s ease!important;
}
.stButton > button:hover {
    border-color:#63b3ed!important; transform:translateY(-1px)!important;
    box-shadow:0 4px 12px rgba(99,179,237,0.2)!important;
}
[data-testid="stFileUploader"] {
    background:rgba(26,39,68,0.4)!important;
    border:1px dashed rgba(99,179,237,0.3)!important; border-radius:10px!important;
}
hr { border-color:rgba(99,179,237,0.12)!important; margin:1rem 0!important; }

@keyframes fadeIn { from{opacity:0;transform:translateY(4px)} to{opacity:1;transform:translateY(0)} }
@keyframes pulse  { 0%,100%{opacity:1} 50%{opacity:0.3} }
.dot { display:inline-block; width:7px; height:7px; border-radius:50%; background:#63b3ed; margin:0 2px; animation:pulse 1.2s infinite; }
.dot:nth-child(2){animation-delay:.2s} .dot:nth-child(3){animation-delay:.4s}
::-webkit-scrollbar{width:5px} ::-webkit-scrollbar-thumb{background:rgba(99,179,237,0.3);border-radius:3px}
</style>
""", unsafe_allow_html=True)


# ── Session state ─────────────────────────────────────────────────────────────
def init_session():
    defaults = {
        "messages":    [],
        "chain":       None,
        "vectorstore": None,
        "stats":       {"chunks": 0, "files": []},
        "db_loaded":   False,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def load_chain():
    with st.spinner("🔄 Loading vector database..."):
        vs = get_vectorstore()
    if vs:
        st.session_state.vectorstore = vs
        st.session_state.chain       = build_rag_chain(vs)
        st.session_state.stats       = get_collection_stats()
        st.session_state.db_loaded   = True
    else:
        st.session_state.db_loaded = False


def run_ingest(reset: bool = False):
    POLICIES_DIR.mkdir(parents=True, exist_ok=True)
    cmd = [sys.executable, "ingest.py"] + (["--reset"] if reset else [])
    with st.spinner("⚙️ Indexing documents — this may take ~30s (embedding locally)..."):
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(Path(__file__).parent))
    if result.returncode == 0:
        st.success("✅ Indexing complete!")
        load_chain()
        st.rerun()
    else:
        st.error(f"❌ Ingestion failed:\n```\n{result.stderr[-2000:]}\n```")


# ── Sidebar ───────────────────────────────────────────────────────────────────
def render_sidebar():
    with st.sidebar:
        st.markdown("### 🛡️ CloudShield AI")
        st.markdown("---")

        badge = "status-ready" if st.session_state.db_loaded else "status-warning"
        label = "● Vector DB Ready" if st.session_state.db_loaded else "● Not Indexed Yet"
        st.markdown(f'<span class="status-badge {badge}">{label}</span>', unsafe_allow_html=True)
        st.markdown("---")

        if st.session_state.db_loaded:
            stats = st.session_state.stats
            c1, c2 = st.columns(2)
            c1.markdown(f'<div class="stat-card"><div class="stat-num">{stats["chunks"]}</div><div class="stat-lbl">Chunks</div></div>', unsafe_allow_html=True)
            c2.markdown(f'<div class="stat-card"><div class="stat-num">{len(stats["files"])}</div><div class="stat-lbl">Files</div></div>', unsafe_allow_html=True)
            st.markdown("**📄 Indexed Files:**")
            for f in stats["files"]:
                st.markdown(f"&nbsp;&nbsp;`{f}`")
            st.markdown("---")

        # Upload PDFs
        st.markdown("### 📤 Upload Policy PDFs")
        uploaded = st.file_uploader("Drop PDFs here", type=["pdf"],
                                    accept_multiple_files=True, label_visibility="collapsed")
        if uploaded:
            POLICIES_DIR.mkdir(parents=True, exist_ok=True)
            saved = []
            for uf in uploaded:
                (POLICIES_DIR / uf.name).write_bytes(uf.read())
                saved.append(uf.name)
            st.success(f"✅ Saved {len(saved)} file(s)")

        # Index buttons
        st.markdown("### ⚙️ Indexing")
        ca, cb = st.columns(2)
        with ca:
            if st.button("▶ Index", use_container_width=True):
                run_ingest(reset=False)
        with cb:
            if st.button("🔄 Re-index", use_container_width=True):
                run_ingest(reset=True)

        # Generate samples
        st.markdown("---")
        st.markdown("### 🧪 Sample Data")
        if st.button("Generate Sample PDFs", use_container_width=True):
            with st.spinner("Generating..."):
                r = subprocess.run([sys.executable, "create_sample_pdfs.py"],
                                   capture_output=True, text=True,
                                   cwd=str(Path(__file__).parent))
            if r.returncode == 0:
                st.success("✅ 3 sample PDFs created!")
                st.info("Click **▶ Index** to embed them.")
            else:
                st.error(r.stderr[-1000:])

        # Clear chat
        st.markdown("---")
        if st.button("🗑️ Clear Conversation", use_container_width=True):
            st.session_state.messages = []
            st.rerun()

        st.markdown("---")
        st.caption("🤖 **LLM**: gpt-4o-mini  \n📐 **Embeddings**: all-MiniLM-L6-v2 (free, local)  \n🗄️ **Vector DB**: ChromaDB")


# ── Hero ──────────────────────────────────────────────────────────────────────
def render_hero():
    st.markdown("""
    <div class="hero-banner">
        <div class="hero-icon">🛡️</div>
        <div>
            <p class="hero-title">CloudShield AI</p>
            <p class="hero-sub">Ask anything about your cloud security policies, compliance guides, and runbooks.
            Answers are grounded in your uploaded documents.</p>
        </div>
    </div>""", unsafe_allow_html=True)


# ── Suggested questions ───────────────────────────────────────────────────────
SUGGESTIONS = [
    "What MFA requirements apply to cloud console access?",
    "What are our RTO and RPO targets for Tier 1 systems?",
    "How should API keys and secrets be stored on AWS?",
    "What is the patch SLA for Critical vulnerabilities?",
    "Explain the SOC 2 change management process.",
    "What logging is required for AWS CloudTrail?",
]

def render_suggestions():
    st.markdown("**💡 Try asking:**")
    cols = st.columns(3)
    for i, q in enumerate(SUGGESTIONS):
        with cols[i % 3]:
            if st.button(q, key=f"sug_{i}", use_container_width=True):
                return q
    return None


# ── Render a single message ───────────────────────────────────────────────────
def render_message(role: str, content: str, sources: list = None):
    avatar = "👤" if role == "user" else "🛡️"
    av_cls = "user" if role == "user" else "bot"
    bub_cls = role  # "user" or "assistant"

    st.markdown(f"""
    <div class="chat-row {role}">
        <div class="avatar {av_cls}">{avatar}</div>
        <div class="bubble {bub_cls}">{content}</div>
    </div>""", unsafe_allow_html=True)

    if sources and role == "assistant":
        with st.expander(f"📄 Sources ({len(sources)} chunks retrieved)"):
            for s in sources:
                pg = f"Page {s['page'] + 1}" if isinstance(s['page'], int) else f"Page {s['page']}"
                st.markdown(f"""
                <div class="source-card">
                    <span class="source-file">📑 {s['file']}</span>
                    <span class="source-page"> — {pg}</span>
                    <div class="source-snippet">{s['snippet']}…</div>
                </div>""", unsafe_allow_html=True)


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    init_session()

    if not st.session_state.db_loaded:
        load_chain()

    render_sidebar()
    render_hero()

    # Not indexed yet
    if not st.session_state.db_loaded:
        st.warning(
            "⚠️ **No documents indexed yet.**\n\n"
            "**Quick start (sidebar):**\n"
            "1. Click **Generate Sample PDFs** → creates 3 demo policy docs\n"
            "2. Click **▶ Index** → embeds them locally (no API cost!)\n"
            "3. Ask your first question!"
        )
        return

    # Chat history
    st.markdown("---")
    if not st.session_state.messages:
        chosen = render_suggestions()
        if chosen:
            st.session_state.messages.append({"role": "user", "content": chosen, "sources": []})
            st.rerun()
    else:
        st.markdown('<div class="chat-wrap">', unsafe_allow_html=True)
        for msg in st.session_state.messages:
            render_message(msg["role"], msg["content"], msg.get("sources"))
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("---")

    # Input
    user_input = st.chat_input("Ask a question about your cloud security policies…")
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input, "sources": []})

        with st.spinner("🛡️ Searching policies and generating answer…"):
            try:
                result  = st.session_state.chain.invoke({"question": user_input})
                answer  = result.get("answer", "No answer generated.")
                sources = format_sources(result.get("source_documents", []))
            except Exception as e:
                answer  = f"❌ Error: {str(e)}"
                sources = []

        st.session_state.messages.append({
            "role": "assistant", "content": answer, "sources": sources
        })
        st.rerun()


if __name__ == "__main__":
    main()
