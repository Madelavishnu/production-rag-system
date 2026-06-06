import os
from dotenv import load_dotenv

from groq import Groq

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

# Load environment variables
load_dotenv()

# Groq client
client = Groq(
    
    api_key=os.getenv("GROQ_API_KEY")
)

# Load PDF
loader = PyPDFLoader(r"data/lab5.pdf")
docs = loader.load()

# Split into chunks
splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=100
)

chunks = splitter.split_documents(docs)

print(f"Total chunks: {len(chunks)}")

# Embedding model
embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# FAISS vector database
vectorstore = FAISS.from_documents(
    chunks,
    embedding_model
)

# User question
query = input("Ask your document: ")

# Retrieve relevant chunks
results = vectorstore.similarity_search(query, k=3)

# Build context
context = "\n\n".join([r.page_content for r in results])

# Prompt
prompt = f"""
You are a helpful AI assistant.

Answer ONLY from the provided context.

If the answer is not in the context, say:
"I could not find the answer in the document."

Context:
{context}

Question:
{query}
"""

# Generate response using Groq
response = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=[
        {
            "role": "user",
            "content": prompt
        }
    ],
    temperature=0
)

# Final answer
answer = response.choices[0].message.content

print("\nANSWER:\n")
print(answer)

print("\nSOURCES:\n")

print("\nSOURCES:\n")

seen = set()

for r in results:
    source = r.metadata.get("source", "Unknown")
    page = r.metadata.get("page", "N/A")

    citation = f"{source} | Page {page + 1}"

    if citation not in seen:
        print(citation)
        seen.add(citation)