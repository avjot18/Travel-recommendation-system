from typing import TypedDict


class TravelState(TypedDict, total=False):

    # Original user query
    query: str

    # Structured understanding of the query
    query_analysis: object

    # Query rewritten for semantic retrieval
    search_query: str

    # Documents retrieved from Chroma
    retrieved_documents: list

    # Documents after ranking
    ranked_destinations: list

    recommendation_decision: dict

    # Generated answer
    answer: str

    # Groundedness result
    grounded: bool
    groundedness_explanation: str

    # Number of regeneration attempts
    retry_count: int