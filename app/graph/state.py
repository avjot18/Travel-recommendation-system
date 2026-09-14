
from typing import TypedDict


class TravelState(TypedDict, total=False):

    # -------------------------------------------------
    # User input
    # -------------------------------------------------

    query: str

    # -------------------------------------------------
    # Query understanding
    # -------------------------------------------------

    query_analysis: object
    search_query: str

    # -------------------------------------------------
    # Retrieval
    # -------------------------------------------------

    retrieved_documents: list

    # -------------------------------------------------
    # Ranking
    # -------------------------------------------------

    ranked_destinations: list

    # -------------------------------------------------
    # Recommendation
    # -------------------------------------------------

    recommendation_decision: dict

    # -------------------------------------------------
    # Structured destination knowledge
    # -------------------------------------------------

    destination_profile: object
    destination_profiles: list

    # -------------------------------------------------
    # Travel planning
    # -------------------------------------------------

    activity_plan: object
    itinerary_plan: object
    budget_plan: object
    stay_area_plan: object

    # -------------------------------------------------
    # Final response
    # -------------------------------------------------

    answer: str

    # -------------------------------------------------
    # Evaluation
    # -------------------------------------------------

    grounded: bool
    groundedness_explanation: str
    retry_count: int
 
