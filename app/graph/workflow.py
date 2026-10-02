from langgraph.graph import StateGraph, START, END

from app.graph.state import TravelState

from app.graph.nodes import (
    analyze_query,
    rewrite_query,
    retrieve_documents,
    rank_destinations,
    evaluate_requirement_fit,
    make_recommendation_decision,
    map_destination,
    detect_weather_requirement,
    get_destination_weather,
    plan_trip,
    generate_answer,
    check_groundedness,
    route_after_recommendation,
    route_after_weather_requirement,
)


def route_after_query_analysis(state):

    travel_profile = state["query_analysis"]

    if travel_profile.intent == "weather_information":
        return "weather"

    return "normal"


def build_graph():

    graph = StateGraph(TravelState)

    # -------------------------
    # Nodes
    # -------------------------

    graph.add_node(
        "analyze_query",
        analyze_query
    )

    graph.add_node(
        "rewrite_query",
        rewrite_query
    )

    graph.add_node(
        "retrieve_documents",
        retrieve_documents
    )

    graph.add_node(
        "rank_destinations",
        rank_destinations
    )

    graph.add_node(
        "evaluate_requirement_fit",
        evaluate_requirement_fit
    )

    graph.add_node(
        "make_recommendation_decision",
        make_recommendation_decision
    )

    graph.add_node(
        "map_destination",
        map_destination
    )

    graph.add_node(
        "detect_weather_requirement",
        detect_weather_requirement
    )

    graph.add_node(
        "get_destination_weather",
        get_destination_weather
    )

    graph.add_node(
        "plan_trip",
        plan_trip
    )

    graph.add_node(
        "generate_answer",
        generate_answer
    )

    graph.add_node(
        "check_groundedness",
        check_groundedness
    )

    # -------------------------
    # Query analysis
    # -------------------------

    graph.add_edge(
        START,
        "analyze_query"
    )

    # -------------------------
    # Query routing
    # -------------------------

    graph.add_conditional_edges(
        "analyze_query",
        route_after_query_analysis,
        {
            "weather": "map_destination",
            "normal": "rewrite_query",
        }
    )

    # -------------------------
    # Normal recommendation
    # pipeline
    # -------------------------

    graph.add_edge(
        "rewrite_query",
        "retrieve_documents"
    )

    graph.add_edge(
        "retrieve_documents",
        "rank_destinations"
    )

    graph.add_edge(
        "rank_destinations",
        "evaluate_requirement_fit"
    )

    graph.add_edge(
        "evaluate_requirement_fit",
        "make_recommendation_decision"
    )

    # -------------------------
    # Recommendation routing
    # -------------------------

    graph.add_conditional_edges(
        "make_recommendation_decision",
        route_after_recommendation,
        {
            "plan_trip": "map_destination",
            "answer": "generate_answer",
        }
    )

    # -------------------------
    # Destination mapping
    # -------------------------

    graph.add_edge(
        "map_destination",
        "detect_weather_requirement"
    )

    # -------------------------
    # Weather routing
    # -------------------------

    graph.add_conditional_edges(
        "detect_weather_requirement",
        route_after_weather_requirement,
        {
            "weather": "get_destination_weather",
            "continue": "plan_trip",
        }
    )

    # -------------------------
    # Live weather
    # -------------------------

    graph.add_edge(
        "get_destination_weather",
        "generate_answer"
    )

    # -------------------------
    # Planning
    # -------------------------

    graph.add_edge(
        "plan_trip",
        "generate_answer"
    )

    # -------------------------
    # Final response
    # -------------------------

    graph.add_edge(
        "generate_answer",
        "check_groundedness"
    )

    graph.add_edge(
        "check_groundedness",
        END
    )

    return graph.compile()