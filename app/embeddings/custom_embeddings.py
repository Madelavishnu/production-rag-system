from sentence_transformers import SentenceTransformer
from langchain_core.embeddings import Embeddings


class CustomEmbeddings(Embeddings):

    def __init__(self):
        self.model = SentenceTransformer(
            "sentence-transformers/all-MiniLM-L6-v2"
        )

    def embed_documents(self, texts):
        embeddings = self.model.encode(texts)
        return [embedding.tolist() for embedding in embeddings]

    def embed_query(self, text):
        embedding = self.model.encode(text)
        return embedding.tolist()