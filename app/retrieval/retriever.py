class HybridRetriever:

    def __init__(self, db):
        self.db = db

    def retrieve(self, query, k=3):

        docs = self.db.similarity_search(query, k=k)

        return [doc.page_content for doc in docs]