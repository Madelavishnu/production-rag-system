from ingestion.loader import load_and_split_pdf

from embeddings.embedding_model import get_embedding_model

from vectorstore.faiss_store import create_or_load_vectorstore

from retrieval.hybrid_retriever import HybridRetriever

from prompts.prompt_template import build_prompt

from llm.groq_client import generate_answer

from retrieval.reranker import Reranker

# Load and split PDF
chunks = load_and_split_pdf(r"data/lab5.pdf")

print(f"Total chunks: {len(chunks)}")

# Embeddings
embedding_model = get_embedding_model()

# Vector DB
vectorstore = create_or_load_vectorstore(
    chunks,
    embedding_model
)

# User query
query = input("Ask your document: ")

# Retrieval
hybrid_retriever = HybridRetriever(vectorstore, chunks)

results = hybrid_retriever.retrieve(
    query,
    k=10
)

reranker = Reranker()

results = reranker.rerank(
    query,
    results,
    top_k=3
)

# Build context
context = ""

for r in results:
    context += f"""
SOURCE: {r.metadata.get('source')} | PAGE: {r.metadata.get('page')}
CONTENT:
{r.page_content}

---
"""

# Prompt
prompt = build_prompt(
    context,
    query
)

# LLM Answer
answer = generate_answer(prompt)

print("\nANSWER:\n")
print(answer)

# Sources
print("\nSOURCES:\n")

seen = set()

for r in results:

    source = r.metadata.get("source", "Unknown")
    page = r.metadata.get("page", "N/A")

    citation = f"{source} | Page {page + 1}"

    if citation not in seen:
        print(citation)
        seen.add(citation)