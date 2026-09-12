from langchain_chroma import Chroma


class TravelVectorStore:

    def __init__(
        self,
        embeddings,
        persist_directory: str,
        collection_name: str
    ):

        self.vector_store = Chroma(
            collection_name=collection_name,
            embedding_function=embeddings,
            persist_directory=persist_directory
        )

    def add_documents(self, documents):

        ids = [document.id for document in documents]

        self.vector_store.add_documents(
            documents=documents,
            ids=ids
        )

    def get_retriever(
        self,
        k: int = 5,
        entity_type: str | None = None
    ):

        search_kwargs = {
            "k": k
        }

        if entity_type:
            search_kwargs["filter"] = {
                "entity_type": entity_type
            }

        return self.vector_store.as_retriever(
            search_type="similarity",
            search_kwargs=search_kwargs
        )