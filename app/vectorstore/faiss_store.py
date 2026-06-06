from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
import os

embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

INDEX_PATH = "faiss_index"


def build_or_load_faiss(documents):

    # Load existing index
    if os.path.exists(INDEX_PATH):
        print("Loading existing FAISS index...")

        db = FAISS.load_local(
            INDEX_PATH,
            embedding_model,
            allow_dangerous_deserialization=True
        )

    else:
        print("Creating new FAISS index...")

        db = FAISS.from_texts(
            documents,
            embedding_model
        )

        db.save_local(INDEX_PATH)

    return db