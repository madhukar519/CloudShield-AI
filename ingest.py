"""
ingest.py — PDF ingestion pipeline.
Loads PDFs → chunks them → embeds (FREE local model) → stores in ChromaDB.

Usage:
    python ingest.py                  # index all PDFs in data/policies/
    python ingest.py --reset          # wipe ChromaDB and re-index from scratch
"""

import argparse
import sys
import time
import os
os.environ["CHROMA_TELEMETRY_GATHER"] = "False"

from pathlib import Path

from dotenv import load_dotenv
load_dotenv()

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
try:
    from langchain_huggingface import HuggingFaceEmbeddings
except ImportError:
    from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_chroma import Chroma

from config import (
    POLICIES_DIR, CHROMA_DIR, CHROMA_COLLECTION,
    CHUNK_SIZE, CHUNK_OVERLAP, EMBEDDING_MODEL
)


def get_embeddings():
    """Load free local HuggingFace embeddings (no API key needed)."""
    print(f"   Loading local embedding model '{EMBEDDING_MODEL}'...", end="", flush=True)
    emb = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={
            "device": "cpu",
            "trust_remote_code": True
        },
        encode_kwargs={"normalize_embeddings": True},
    )
    print(" [OK]")
    return emb


def load_pdfs(directory: Path) -> list:
    """Load all PDF files from the given directory."""
    pdf_files = list(directory.glob("*.pdf"))
    if not pdf_files:
        print(f"[WARN] No PDF files found in {directory}")
        print("   Run  python create_sample_pdfs.py  first to generate sample PDFs.")
        sys.exit(1)

    print(f"\n[DIR] Found {len(pdf_files)} PDF file(s):")
    all_docs = []
    for pdf_path in pdf_files:
        print(f"   Loading: {pdf_path.name} ...", end="", flush=True)
        try:
            loader = PyPDFLoader(str(pdf_path))
            docs = loader.load()
            for doc in docs:
                doc.metadata["source_file"] = pdf_path.name
            all_docs.extend(docs)
            print(f" [OK] ({len(docs)} pages)")
        except Exception as e:
            print(f" [FAIL] Error: {e}")

    return all_docs


def chunk_documents(docs: list) -> list:
    """Split documents into overlapping chunks."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
        length_function=len,
    )
    return splitter.split_documents(docs)


def build_vectorstore(chunks: list, reset: bool = False) -> Chroma:
    """Embed chunks and store them in ChromaDB."""
    CHROMA_DIR.mkdir(parents=True, exist_ok=True)

    if reset:
        try:
            import chromadb
            import chromadb.config
            client = chromadb.PersistentClient(
                path=str(CHROMA_DIR),
                settings=chromadb.config.Settings(anonymized_telemetry=False)
            )
            # Delete and recreate the collection to clear it
            try:
                client.delete_collection(CHROMA_COLLECTION)
            except (ValueError, Exception):
                pass
            print("[CLEAN] Cleared existing ChromaDB collection via Client API.")
        except Exception as e:
            print(f"[WARN] Could not reset via API: {e}. If the DB is locked, please stop Streamlit first.")

    embeddings = get_embeddings()

    print(f"\n[STEP] Embedding {len(chunks)} chunks locally (no API calls)...\n")

    batch_size = 50
    vectorstore = None
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i: i + batch_size]
        batch_num = i // batch_size + 1
        total_batches = (len(chunks) + batch_size - 1) // batch_size
        print(f"   Batch {batch_num}/{total_batches} ({len(batch)} chunks)...", end="", flush=True)

        if vectorstore is None:
            import chromadb.config
            vectorstore = Chroma(
                collection_name=CHROMA_COLLECTION,
                embedding_function=embeddings,
                client_settings=chromadb.config.Settings(anonymized_telemetry=False),
                persist_directory=str(CHROMA_DIR),
            )
        else:
            vectorstore.add_documents(batch)

        print(" [OK]")

    return vectorstore


def print_summary(docs: list, chunks: list, elapsed: float):
    files = set(d.metadata.get("source_file", "unknown") for d in docs)
    print("\n" + "-" * 55)
    print("  [SUCCESS] INGESTION COMPLETE")
    print("-" * 55)
    print(f"  [FILES] Files indexed  : {len(files)}")
    print(f"  [PAGES] Total pages    : {len(docs)}")
    print(f"  [CHUNKS] Total chunks   : {len(chunks)}")
    print(f"  [TIME] Time elapsed   : {elapsed:.1f}s")
    print(f"  [STORE] Stored in      : {CHROMA_DIR}")
    print("-" * 55)
    print("\nNext step: Run 'streamlit run app.py' to start the chatbot.\n")


def main():
    parser = argparse.ArgumentParser(description="Ingest PDFs into ChromaDB")
    parser.add_argument("--reset", action="store_true",
                        help="Wipe existing ChromaDB and re-index from scratch")
    args = parser.parse_args()

    print("[START] Cloud Security Policy Chatbot — PDF Ingestion Pipeline")
    print("-" * 55)

    start  = time.time()
    docs   = load_pdfs(POLICIES_DIR)
    chunks = chunk_documents(docs)
    print(f"\n[CHUNK] Chunked into {len(chunks)} segments "
          f"(size={CHUNK_SIZE} chars, overlap={CHUNK_OVERLAP} chars)")

    build_vectorstore(chunks, reset=args.reset)
    print_summary(docs, chunks, time.time() - start)


if __name__ == "__main__":
    main()
