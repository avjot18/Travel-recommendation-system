from langgraph.graph import StateGraph, START, END

from app.graph.state import TravelState

from app.graph.nodes import (
    analyze_query,
    rewrite_query,
    retrieve_documents,
    rank_destinations,
    evaluate_requirement_fit,
    make_recommendation_decision,
    generate_answer,
    check_groundedness,
)


def build_graph():

    graph = StateGraph(TravelState)

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
    "make_recommendation_decision",
    make_recommendation_decision
)

    graph.add_node(
        "evaluate_requirement_fit",
        evaluate_requirement_fit
    )

    graph.add_node(
        "generate_answer",
        generate_answer
    )

    graph.add_node(
        "check_groundedness",
        check_groundedness
    )

    graph.add_edge(
        START,
        "analyze_query"
    )

    graph.add_edge(
        "analyze_query",
        "rewrite_query"
    )

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

    graph.add_edge(
    "make_recommendation_decision",
    "generate_answer"
)

    graph.add_edge(
        "generate_answer",
        "check_groundedness"
    )

    graph.add_edge(
        "check_groundedness",
        END
    )

    return graph.compile()