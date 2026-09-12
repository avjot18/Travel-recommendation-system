from app.query.analyzer import QueryAnalyzer
from app.retrieval.embeddings import EmbeddingService
from app.retrieval.vector_store import TravelVectorStore
from app.ranking.ranker import DestinationRanker
from app.query.rewriter import QueryRewriter
from app.generation.answer_generator import AnswerGenerator
from app.evaluation.groundedness_checker import GroundednessChecker


CHROMA_PATH = "data/chroma"
COLLECTION_NAME = "india_travel"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


def main():

    print("Starting application...")

    # 1. Load embedding model
    embedding_service = EmbeddingService(
        EMBEDDING_MODEL
    )

    embeddings = embedding_service.get_embeddings()

    # 2. Connect to Chroma
    vector_store = TravelVectorStore(
        embeddings=embeddings,
        persist_directory=CHROMA_PATH,
        collection_name=COLLECTION_NAME
    )

    # 3. Create Query Analyzer
    analyzer = QueryAnalyzer(
        "qwen3:8b"
    )

    # 4. User query
    query = """
    I have 4 days and want a peaceful mountain
    trip with my girlfriend. My budget is low.
    I don't want extreme cold.
    """

    # 5. Analyze query
    analysis = analyzer.analyze(query)

    print("\nQuery Analysis:")
    print(analysis)

    # 6. Create search query
    rewriter = QueryRewriter(
    "qwen3:8b"
)

    search_query = rewriter.rewrite(
        analysis
    )

    print("\nSearch Query:")
    print(search_query)

    # 7. Retrieve candidates from Chroma
    retriever = vector_store.get_retriever(
        k=5,
        entity_type="destination"
    )

    documents = retriever.invoke(search_query)

    # 8. Rank candidates
    ranker = DestinationRanker()

    ranked_destinations = ranker.rank(
        documents,
        analysis
    )

    # 9. Show ranked results
    print("\nRanked Destinations:")
    print("--------------------")

    for item in ranked_destinations:

        document = item["document"]
        score = item["score"]

        print(
            f"\nDestination: "
            f"{document.metadata.get('destination')}"
        )

        print(
            f"State: "
            f"{document.metadata.get('state')}"
        )

        print(
            f"Score: {score}"
        )

        # 10. Generate final answer
    answer_generator = AnswerGenerator(
        "qwen3:8b"
    )

    answer = answer_generator.generate(
        query=query,
        query_analysis=analysis,
        ranked_destinations=ranked_destinations
    )

    print("\nFinal Answer:")
    print("--------------------")
    print(answer)    

        # 11. Check answer groundedness
    groundedness_checker = GroundednessChecker(
        "qwen3:8b"
    )

    groundedness = groundedness_checker.check(
        answer=answer,
        documents=[item["document"] for item in ranked_destinations]
    )

    print("\nGroundedness Check:")
    print("--------------------")
    print(groundedness)


if __name__ == "__main__":
    main()