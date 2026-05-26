from functools import lru_cache
import os

from .config import CHROMA_DIR, GEMINI_API_KEY

DB_PATH = str(CHROMA_DIR)


@lru_cache(maxsize=1)
def _get_client():
    from google import genai
    if not GEMINI_API_KEY:
        raise RuntimeError("Missing GEMINI_API_KEY in environment (.env).")
    return genai.Client(api_key=GEMINI_API_KEY)


@lru_cache(maxsize=1)
def _get_embeddings():
    from langchain_community.embeddings import HuggingFaceEmbeddings
    return HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")


def _get_db():
    from langchain_community.vectorstores import Chroma
    return Chroma(persist_directory=DB_PATH, embedding_function=_get_embeddings())


def query_rag(question):
    from google.genai import errors as genai_errors

    db = _get_db()
    results = db.similarity_search(question, k=2)

    context = "\n\n".join([doc.page_content for doc in results])
    max_context_chars = int(os.getenv("MAX_CONTEXT_CHARS", "4000"))
    if len(context) > max_context_chars:
        context = context[:max_context_chars] + "\n\n[...truncated...]"

    prompt = f"""
    You are a helpful AI assistant.

    Answer the question using ONLY the context below.

    Context:
    {context}

    Question:
    {question}
    """

    try:
        response = _get_client().models.generate_content(
            model=os.getenv("GEMINI_MODEL", "gemini-2.0-flash"),
            contents=prompt,
        )
        return response.text
    except genai_errors.ClientError as e:
        # Common case during demos: free-tier quota / rate limit exceeded (HTTP 429).
        msg = str(e)
        if "429" in msg or "RESOURCE_EXHAUSTED" in msg:
            # Keep the app usable even when quota is exhausted by returning
            # an extractive response from the retrieved context.
            return (
                "Gemini quota exhausted (HTTP 429 RESOURCE_EXHAUSTED). "
                "Showing relevant context from your documents instead:\n\n"
                f"{context}"
            )
        raise RuntimeError(f"Gemini API error: {e}") from e
