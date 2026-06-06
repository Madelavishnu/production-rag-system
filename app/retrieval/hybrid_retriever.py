class HybridRetriever:

    def __init__(self, index):
        self.index = index

    def retrieve(self, query, k=3):

        docs = self.index.similarity_search(query, k=k)

        unique_docs = []
        seen = set()

        for doc in docs:
            content = doc.page_content

            if content not in seen:
                seen.add(content)
                unique_docs.append(content)

        return unique_docs