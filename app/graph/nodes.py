import time

from app.core.services import ExploreEaseServices


# Load all expensive services once
services = ExploreEaseServices()


def analyze_query(state):

    start = time.time()

    analysis = services.analyzer.analyze(
        state["query"]
    )

    print(f"[TIME] analyze_query: {time.time() - start:.2f}s")

    return {
        "query_analysis": analysis
    }


def rewrite_query(state):

    start = time.time()

    search_query = services.rewriter.rewrite(
        state["query_analysis"]
    )

    print(f"[TIME] rewrite_query: {time.time() - start:.2f}s")

    return {
        "search_query": search_query
    }


def retrieve_documents(state):

    start = time.time()

    retriever = services.vector_store.get_retriever(
        k=5,
        entity_type="destination"
    )

    documents = retriever.invoke(
        state["search_query"]
    )

    print(f"[TIME] retrieve_documents: {time.time() - start:.2f}s")

    return {
        "retrieved_documents": documents
    }


def rank_destinations(state):

    start = time.time()

    ranked_destinations = services.ranker.rank(
        state["retrieved_documents"],
        state["query_analysis"]
    )

    print(f"[TIME] rank_destinations: {time.time() - start:.2f}s")

    return {
        "ranked_destinations": ranked_destinations
    }

def make_recommendation_decision(state):
    start = time.time()

    decision = services.recommendation_decision.decide(
        state["ranked_destinations"]
    )

    candidate = decision["candidate"]

    if candidate:
        print("\nRECOMMENDATION DECISION:")
        print("------------------------")
        print("Destination:",
              candidate["document"].metadata.get("destination"))
        print("Status:", decision["status"])
        print("Score:", candidate["score"])

    print(
        f"[TIME] make_recommendation_decision: "
        f"{time.time() - start:.2f}s"
    )

    return {
        "recommendation_decision": decision
    }


def evaluate_requirement_fit(state):

    start = time.time()

    evaluated_destinations = (
        services.requirement_fit.evaluate(
            state["ranked_destinations"]
        )
    )

    for item in evaluated_destinations[:3]:

        print("\nDESTINATION:")
        print(
            item["document"].metadata.get("destination")
        )

        print(
            "SCORE:",
            item["score"]
        )

        print(
            "FIT:",
            item["requirement_fit"]
        )

    print(
        f"[TIME] evaluate_requirement_fit: "
        f"{time.time() - start:.2f}s"
    )

    return {
        "ranked_destinations": evaluated_destinations
    }

def generate_answer(state):
    start = time.time()

    answer = services.generator.generate(
        query=state["query"],
        query_analysis=state["query_analysis"],
        recommendation_decision=state["recommendation_decision"]
    )

    print(
        f"[TIME] generate_answer: "
        f"{time.time() - start:.2f}s"
    )

    return {
        "answer": answer
    }
def check_groundedness(state):

    start = time.time()

    result = services.groundedness_checker.check(
    answer=state["answer"],
    documents=state["retrieved_documents"],
    requirement_fit=(
        state["recommendation_decision"]
        ["candidate"]
        ["requirement_fit"]
    )
)

    print(
        f"[TIME] check_groundedness: "
        f"{time.time() - start:.2f}s"
    )

    print("\nCLAIM EVALUATION:")
    print("------------------------")

    for claim in result.claims:

        print(
            f"{claim.classification}: "
            f"{claim.claim}"
        )

    return {
        "grounded": result.grounded,
        "groundedness_explanation": result.explanation
    }