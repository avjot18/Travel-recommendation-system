import time

from app.core.services import ExploreEaseServices
from app.tools.destination_weather import (
    DestinationWeatherTool,
)


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
        recommendation_decision=state.get(
            "recommendation_decision"
        ),
        destination_weather=state.get(
            "destination_weather"
        ),
        destination_profile=state.get(
            "destination_profile"
        ),
        activity_plan=state.get(
            "activity_plan"
        ),
        itinerary_plan=state.get(
            "itinerary_plan"
        ),
        budget_plan=state.get(
            "budget_plan"
        ),
        stay_area_plan=state.get(
            "stay_area_plan"
        ),
    )

    print(
        f"[TIME] generate_answer: "
        f"{time.time() - start:.2f}s"
    )

    return {
        "answer": answer
    }
def check_groundedness(state):

    print("\nGROUNDEDNESS CHECK:")
    print("------------------------")
    print("Skipped during V2 graph development.")

    return {
        "grounded": True,
        "groundedness_explanation": (
            "Groundedness evaluation temporarily "
            "disabled during V2 graph development."
        )
    }

def map_destination(state):

    start = time.time()

    travel_profile = state.get(
        "query_analysis"
    )

    decision = state.get(
        "recommendation_decision",
        {}
    )

    candidate = decision.get(
        "candidate"
    )

    # -------------------------------------------------
    # MODE 1:
    # Recommendation / trip-planning query
    # -------------------------------------------------

    if candidate:

        document = candidate[
            "document"
        ]

        destination_id = (
            document.metadata.get(
                "destination_id"
            )
        )

        destination_profile = (
            services.destination_mapper.document_to_profile(
                document
            )
        )

        print(
            "\nDESTINATION MAPPING:"
        )

        print(
            "Destination:",
            document.metadata.get(
                "destination"
            )
        )

        print(
            "Destination ID:",
            destination_id
        )

        print(
            "Profile mapped:",
            "YES" if destination_profile else "NO"
        )

        print(
            f"[TIME] map_destination: "
            f"{time.time() - start:.2f}s"
        )

        return {
            "destination_profile":
                destination_profile
        }

    # -------------------------------------------------
    # MODE 2:
    # Direct destination query
    #
    # Example:
    # "What will the weather be like in Manali?"
    # -------------------------------------------------

    location = None

    if travel_profile:

        location = travel_profile.location

    if not location:

        print(
            "\nDESTINATION MAPPING:"
        )

        print(
            "No recommendation candidate "
            "or explicit destination available."
        )

        print(
            f"[TIME] map_destination: "
            f"{time.time() - start:.2f}s"
        )

        return {
            "destination_profile": None
        }

    destination_profile = (
        services.destination_repository
        .get_destination_by_name(
            location
        )
    )

    # -------------------------------------------------
    # Destination not found
    # -------------------------------------------------

    if destination_profile is None:

        print(
            "\nDESTINATION MAPPING:"
        )

        print(
            "Could not find destination:",
            location
        )

        print(
            f"[TIME] map_destination: "
            f"{time.time() - start:.2f}s"
        )

        return {
            "destination_profile": None
        }

    # -------------------------------------------------
    # Direct destination mapping
    # -------------------------------------------------

    print(
        "\nDESTINATION MAPPING:"
    )

    print(
        "Destination:",
        destination_profile.name
    )

    print(
        "Destination ID:",
        destination_profile.destination_id
    )

    print(
        "Profile mapped: YES"
    )

    print(
        f"[TIME] map_destination: "
        f"{time.time() - start:.2f}s"
    )

    return {
        "destination_profile":
            destination_profile
    }
 
def detect_weather_requirement(state):

    start = time.time()

    travel_profile = state.get(
        "query_analysis"
    )

    if travel_profile is None:

        print(
            "\nWEATHER REQUIREMENT:"
        )
        print(
            "Query analysis unavailable."
        )

        return {
            "weather_required": False
        }

    weather_required = (
        travel_profile.needs_live_weather
    )

    print(
        "\nWEATHER REQUIREMENT:"
    )
    print(
        "Live weather required:",
        weather_required
    )

    print(
        f"[TIME] detect_weather_requirement: "
        f"{time.time() - start:.2f}s"
    )

    return {
        "weather_required":
            weather_required
    }


def get_destination_weather(state):

    start = time.time()

    destination = state.get(
        "destination_profile"
    )

    if destination is None:

        print(
            "\nLIVE WEATHER:"
        )
        print(
            "Destination profile unavailable."
        )

        return {
            "destination_weather": None
        }

    print(
        "\nLIVE WEATHER:"
    )
    print(
        "Destination:",
        destination.name
    )
    print(
        "State:",
        destination.state_or_ut
    )

    weather_tool = DestinationWeatherTool()

    weather = weather_tool.get_weather(
        destination=destination.name,
        state=destination.state_or_ut,
        forecast_days=7,
    )

    print(
        "Weather fetched successfully."
    )

    print(
        "Temperature:",
        weather.weather.temperature_c,
        "°C"
    )

    print(
        f"[TIME] get_destination_weather: "
        f"{time.time() - start:.2f}s"
    )

    return {
        "destination_weather":
            weather
    }
def plan_trip(state):

    start = time.time()

    travel_profile = state[
        "query_analysis"
    ]

    destination = state.get(
        "destination_profile"
    )

    # -------------------------------------------------
    # No destination available
    # -------------------------------------------------

    if destination is None:

        print(
            "\nTRAVEL PLANNING:"
        )

        print(
            "No destination profile available."
        )

        print(
            f"[TIME] plan_trip: "
            f"{time.time() - start:.2f}s"
        )

        return {
            "activity_plan": None,
            "itinerary_plan": None,
            "budget_plan": None,
            "stay_area_plan": None
        }

    # -------------------------------------------------
    # Activity planning
    # -------------------------------------------------

    activity_plan = (
        services.activity_planner.plan(
            travel_profile,
            destination
        )
    )

    # -------------------------------------------------
    # Itinerary planning
    # -------------------------------------------------

    itinerary_plan = (
        services.itinerary_planner.plan(
            travel_profile,
            destination,
            activity_plan
        )
    )

    # -------------------------------------------------
    # Budget estimation
    # -------------------------------------------------

    budget_plan = (
        services.budget_estimator.estimate(
            travel_profile,
            destination
        )
    )

    # -------------------------------------------------
    # Stay area recommendation
    # -------------------------------------------------

    stay_area_plan = (
        services.stay_area_recommender.recommend(
            travel_profile,
            destination
        )
    )

    # -------------------------------------------------
    # Display planning summary
    # -------------------------------------------------

    print(
        "\nTRAVEL PLAN:"
    )
    print(
        "-------------"
    )

    print(
        "Destination:",
        destination.name
    )

    print(
        "Activities:",
        len(activity_plan.activities)
    )

    print(
        "Itinerary days:",
        len(itinerary_plan.days)
    )

    print(
        "Budget:",
        budget_plan.total
    )

    print(
        "Budget status:",
        budget_plan.total_status
    )

    print(
        "Stay area status:",
        stay_area_plan.status
    )

    print(
        f"[TIME] plan_trip: "
        f"{time.time() - start:.2f}s"
    )

    return {
        "activity_plan": activity_plan,
        "itinerary_plan": itinerary_plan,
        "budget_plan": budget_plan,
        "stay_area_plan": stay_area_plan
    }
def route_after_recommendation(state):
    travel_profile = state["query_analysis"]

    intent = travel_profile.intent

    if intent == "destination_comparison":
        return "answer"

    if (
        travel_profile.duration_days
        or travel_profile.activities
        or travel_profile.must_have_activities
    ):
        return "plan_trip"

    return "answer"
 
def route_after_weather_requirement(state):

    if state.get(
        "weather_required",
        False,
    ):
        return "weather"

    return "continue"
# def check_groundedness(state):

#     start = time.time()

#     result = services.groundedness_checker.check(
#     answer=state["answer"],
#     documents=state["retrieved_documents"],
#     requirement_fit=(
#         state["recommendation_decision"]
#         ["candidate"]
#         ["requirement_fit"]
#     )
# )

#     print(
#         f"[TIME] check_groundedness: "
#         f"{time.time() - start:.2f}s"
#     )

#     print("\nCLAIM EVALUATION:")
#     print("------------------------")

#     for claim in result.claims:

#         print(
#             f"{claim.classification}: "
#             f"{claim.claim}"
#         )

#     return {
#         "grounded": result.grounded,
#         "groundedness_explanation": result.explanation
#     }