from rank_bm25 import BM25Okapi

class BM25Retriever:
    def __init__(self, documents):
        self.documents = documents
        tokenized_docs = [doc.split() for doc in documents]
        self.bm25 = BM25Okapi(tokenized_docs)

    def retrieve(self, query, k=3):
        tokenized_query = query.split()

        scores = self.bm25.get_scores(tokenized_query)

        ranked_docs = sorted(
            zip(self.documents, scores),
            key=lambda x: x[1],
            reverse=True
        )

        return [doc for doc, score in ranked_docs[:k]]