import os
os.environ["CHROMA_TELEMETRY_GATHER"] = "False"

from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

try:
    from langchain_huggingface import HuggingFaceEmbeddings
except ImportError:
    from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.documents import Document

from config import (
    CHROMA_DIR, CHROMA_COLLECTION, EMBEDDING_MODEL,
    LLM_MODEL, LLM_TEMPERATURE, LLM_MAX_TOKENS,
    MODEL_PROVIDER, BEDROCK_MODEL, BEDROCK_REGION,
    TOP_K, SYSTEM_PROMPT
)


def _get_embeddings():
    return HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={
            "device": "cpu",
            "trust_remote_code": True
        },
        encode_kwargs={"normalize_embeddings": True},
    )


def get_vectorstore() -> Chroma | None:
    """Load existing ChromaDB using a direct client for stability."""
    if not CHROMA_DIR.exists() or not any(CHROMA_DIR.iterdir()):
        return None
    try:
        import chromadb
        import chromadb.config
        # Create client directly to avoid RustBindingsAPI errors and disable telemetry
        client = chromadb.PersistentClient(
            path=str(CHROMA_DIR),
            settings=chromadb.config.Settings(anonymized_telemetry=False)
        )
        
        vectorstore = Chroma(
            collection_name=CHROMA_COLLECTION,
            embedding_function=_get_embeddings(),
            client=client,
        )
        count = vectorstore._collection.count()
        return vectorstore if count > 0 else None
    except Exception as e:
        print(f"[ERROR] Could not load vectorstore: {e}")
        return None


def get_collection_stats() -> dict:
    """Return stats about the loaded ChromaDB collection."""
    try:
        import chromadb
        import chromadb.config
        client = chromadb.PersistentClient(
            path=str(CHROMA_DIR),
            settings=chromadb.config.Settings(anonymized_telemetry=False)
        )
        vectorstore = Chroma(
            collection_name=CHROMA_COLLECTION,
            embedding_function=_get_embeddings(),
            client=client,
        )
        count = vectorstore._collection.count()
        if count > 0:
            results = vectorstore._collection.get(include=["metadatas"])
            files = set()
            for meta in results["metadatas"]:
                if meta and "source_file" in meta:
                    files.add(meta["source_file"])
            return {"chunks": count, "files": list(files)}
        return {"chunks": 0, "files": []}
    except Exception:
        return {"chunks": 0, "files": []}


def _format_docs(docs: list[Document]) -> str:
    """Format retrieved docs into a single context string."""
    parts = []
    for i, doc in enumerate(docs, 1):
        src  = doc.metadata.get("source_file", "Unknown")
        page = doc.metadata.get("page", "?")
        page_label = f"Page {page + 1}" if isinstance(page, int) else f"Page {page}"
        parts.append(f"[Source {i}: {src} — {page_label}]\n{doc.page_content}")
    return "\n\n---\n\n".join(parts)


def build_rag_chain(vectorstore: Chroma):
    """Build a simple LCEL RAG chain (LangChain 1.x compatible)."""
    retriever = vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": TOP_K},
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("human", "{question}"),
    ])

    if MODEL_PROVIDER == "openai":
        llm = ChatOpenAI(
            model=LLM_MODEL,
            temperature=LLM_TEMPERATURE,
            max_tokens=LLM_MAX_TOKENS,
        )
    elif MODEL_PROVIDER == "bedrock":
        try:
            from langchain_aws import ChatBedrockConverse
            llm = ChatBedrockConverse(
                model=BEDROCK_MODEL,
                region_name=BEDROCK_REGION,
                temperature=LLM_TEMPERATURE,
                max_tokens=LLM_MAX_TOKENS,
            )
        except ImportError:
            raise ImportError(
                "Please install 'langchain-aws' and 'boto3' to use Bedrock: "
                "pip install langchain-aws boto3"
            )
    else:
        raise ValueError(f"Unknown MODEL_PROVIDER: {MODEL_PROVIDER}")

    # Store retrieved docs in a side channel
    def retrieve_and_format(inputs):
        question = inputs["question"]
        docs = retriever.invoke(question)
        return {
            "context":  _format_docs(docs),
            "question": question,
            "_docs":    docs,
        }

    chain = (
        RunnablePassthrough()
        | retrieve_and_format
        | {
            "answer": (
                lambda x: {"context": x["context"], "question": x["question"]}
            ) | prompt | llm | StrOutputParser(),
            "source_documents": lambda x: x["_docs"],
        }
    )

    return chain


def format_sources(docs: list[Document]) -> list[dict]:
    """Format source documents into display-ready dicts."""
    sources = []
    seen = set()
    for doc in docs:
        meta      = doc.metadata
        file_name = meta.get("source_file", meta.get("source", "Unknown"))
        page      = meta.get("page", "N/A")
        key       = f"{file_name}::{page}"
        if key not in seen:
            seen.add(key)
            sources.append({
                "file":    file_name,
                "page":    page,
                "snippet": doc.page_content[:300].strip(),
            })
    return sources
