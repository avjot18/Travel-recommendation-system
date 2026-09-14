from app.destination.repository import (
    DestinationRepository
)

from app.destination.mapper import (
    DestinationMapper
)

from app.retrieval.embeddings import (
    EmbeddingService
)

from app.retrieval.vector_store import (
    TravelVectorStore
)


DATA_PATH = (
    "data/"
    "india_travel_knowledge_base_v2_fully_populated.json"
)

CHROMA_PATH = "data/chroma"

COLLECTION_NAME = "india_travel"

EMBEDDING_MODEL = (
    "sentence-transformers/"
    "all-MiniLM-L6-v2"
)


def main():

    repository = DestinationRepository(
        DATA_PATH
    )

    mapper = DestinationMapper(
        repository
    )

    embedding_service = (
        EmbeddingService(
            EMBEDDING_MODEL
        )
    )

    embeddings = (
        embedding_service.get_embeddings()
    )

    vector_store = TravelVectorStore(
        embeddings=embeddings,
        persist_directory=CHROMA_PATH,
        collection_name=COLLECTION_NAME
    )

    retriever = (
        vector_store.get_retriever(
            k=5,
            entity_type="destination"
        )
    )

    documents = retriever.invoke(
        "peaceful mountain trip for couples"
    )

    print("\nRETRIEVED DOCUMENTS")
    print("===================")

    for document in documents:

        print(
            document.metadata.get(
                "destination"
            )
        )

    profiles = (
        mapper.documents_to_profiles(
            documents
        )
    )

    print("\nMAPPED DESTINATION PROFILES")
    print("===========================")

    for profile in profiles:

        print(
            profile.name,
            "->",
            profile.destination_id
        )

    print(
        f"\nProfiles mapped: "
        f"{len(profiles)}"
    )


if __name__ == "__main__":
    main()