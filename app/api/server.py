from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import os
import fitz
import json
import time

from dotenv import load_dotenv
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_core.embeddings import Embeddings

from sentence_transformers import SentenceTransformer
from fastapi.middleware.cors import CORSMiddleware


from groq import Groq


# =========================
# FASTAPI
# =========================


chat_history = []
if os.path.exists("pdfs.json"):
    with open("pdfs.json", "r") as f:
        uploaded_pdfs = json.load(f)
else:
    uploaded_pdfs = []

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================
# GROQ
# =========================


load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


# =========================
# EMBEDDINGS
# =========================

class CustomEmbeddings(Embeddings):

    def __init__(self):
        self.model = SentenceTransformer(
            "sentence-transformers/all-MiniLM-L6-v2"
        )

    def embed_documents(self, texts):
        embeddings = self.model.encode(texts)
        return [e.tolist() for e in embeddings]

    def embed_query(self, text):
        embedding = self.model.encode(text)
        return embedding.tolist()


embeddings = CustomEmbeddings()



# =========================
# GLOBAL VECTORSTORE
# =========================

vectorstore = None

# Load existing FAISS database if available
if os.path.exists("faiss_db"):
    try:
        vectorstore = FAISS.load_local(
            "faiss_db",
            embeddings,
            allow_dangerous_deserialization=True
        )

        print("✅ FAISS database loaded successfully")

    except Exception as e:
        print("❌ Error loading FAISS:", e)


# =========================
# REQUEST MODEL
# =========================

class QuestionRequest(BaseModel):
    question: str


# =========================
# PDF TEXT EXTRACTION
# =========================

def extract_text_from_pdf(pdf_path):

    doc = fitz.open(pdf_path)

    text = ""

    for page in doc:
        text += page.get_text()

    return text


# =========================
# HOME
# =========================

@app.get("/")
def home():
    return {"message": "RAG Application Running"}


# =========================
# UPLOAD PDF
# =========================

@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):

    global vectorstore
    global uploaded_pdfs

    os.makedirs("data", exist_ok=True)

    file_path = f"data/{file.filename}"

    with open(file_path, "wb") as f:
        f.write(await file.read())

    uploaded_pdfs.append(file.filename)

    print("Uploaded PDFs:", uploaded_pdfs)

    print("Current Directory:", os.getcwd())

    with open("pdfs.json", "w") as f:
        json.dump(uploaded_pdfs, f)

    # Extract PDF text
    text = extract_text_from_pdf(file_path)

    # Split text
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )

    docs = splitter.create_documents(
        [text],
        metadatas=[
            {
                "source": file.filename
            }
        ]
    )
    print(docs[0].metadata)

    print("Total Chunks:", len(docs))

    # Create FAISS Vector DB
    if vectorstore is None:

        vectorstore = FAISS.from_documents(
            docs,
            embeddings
        )

        vectorstore.save_local("faiss_db")

    else:

        vectorstore.add_documents(docs)

        vectorstore.save_local("faiss_db")

    return {
        "message": "PDF uploaded successfully",
        "chunks": len(docs),
        "pdfs": uploaded_pdfs,
        "total_pdfs": len(uploaded_pdfs)
    }


history_text = ""

for item in chat_history[-5:]:
    history_text += f"User: {item['question']}\n"
    history_text += f"Assistant: {item['answer']}\n\n"

# =========================
# ASK QUESTION
# =========================

# =========================
# ASK QUESTION
# =========================
@app.get("/status")
def status():

    return {
        "uploaded_pdfs": uploaded_pdfs,
        "total_pdfs": len(uploaded_pdfs),
        "vectorstore_loaded": vectorstore is not None
    }
@app.post("/clear")
def clear_database():

    global vectorstore
    global uploaded_pdfs
    global chat_history

    vectorstore = None
    uploaded_pdfs = []
    chat_history = []

    vectorstore = None

    if os.path.exists("faiss_db"):
        import shutil
        shutil.rmtree("faiss_db")
    
    with open("pdfs.json", "w") as f:
        json.dump(uploaded_pdfs, f)

    return {
        "message": "Database cleared"
    }


@app.post("/ask")
def ask_question(request: QuestionRequest):

    global vectorstore
    global chat_history

    if vectorstore is None:
        return {
            "error": "Please upload PDF first"
        }

    question = request.question

    # Build conversation history
    history_text = ""

    for item in chat_history[-5:]:
        history_text += f"User: {item['question']}\n"
        history_text += f"Assistant: {item['answer']}\n\n"

    # Retrieve docs with scores
    retrieved_docs_with_scores = vectorstore.similarity_search_with_score(
        question,
        k=3
    )

    docs = []
    scores = []

    for doc, score in retrieved_docs_with_scores:
        docs.append(doc)
        scores.append(score)

    print("Similarity Scores:", scores)

    for doc in docs:
        print("Metadata:", doc.metadata)

    # Relevance filter
    best_score = scores[0]

    if best_score > 1.7:
        return {
            "question": question,
            "answer": "I could not find relevant information in the uploaded PDF.",
            "documents": []
        }

    # Context
    context = "\n\n".join(
        [doc.page_content for doc in docs]
    )

    prompt = f"""
Previous Conversation:
{history_text}

Context:
{context}

Current Question:
{question}

Instructions:
- Answer only using the provided context.
- If the answer is not present in the context, say:
  "I could not find this information in the uploaded PDF."

Answer:
"""

    # GROQ RESPONSE
    start_time = time.time()
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.3
    )

    

    answer = response.choices[0].message.content

    end_time = time.time()

    response_time = round(
        end_time - start_time,
        2
    )

    # Save memory
    chat_history.append({
        "question": question,
        "answer": answer,
        "response_time": response_time
    })
    

    return {
        "question": question,
        "answer": answer,
        "documents": [
            {
                "pdf": doc.metadata.get("source"),
                "content": doc.page_content[:200] + "...",
                "score": float(score)
            }
            for doc, score in retrieved_docs_with_scores
        ],
        "response_time" : response_time
        
    }