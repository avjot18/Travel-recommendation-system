from app.ingestion.loader import TravelDatasetLoader
from app.retrieval.embeddings import EmbeddingService
from app.retrieval.vector_store import TravelVectorStore


DATA_PATH = "data/india_travel_knowledge_base_v2_fully_populated.json"
CHROMA_PATH = "data/chroma"
COLLECTION_NAME = "india_travel"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


def main():

    print("Starting ingestion...")

    # 1. Load documents
    loader = TravelDatasetLoader(DATA_PATH)

    documents = loader.load()

    print(f"Loaded {len(documents)} documents")


    # 2. Create embedding service
    embedding_service = EmbeddingService(
        EMBEDDING_MODEL
    )

    embeddings = embedding_service.get_embeddings()


    # 3. Create Chroma vector store
    vector_store = TravelVectorStore(
        embeddings=embeddings,
        persist_directory=CHROMA_PATH,
        collection_name=COLLECTION_NAME
    )


    # 4. Add documents to Chroma
    vector_store.add_documents(documents)

    print("Ingestion completed!")


if __name__ == "__main__":
    main()