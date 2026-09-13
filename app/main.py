from app.graph.workflow import build_graph


def main():

    print("Starting ExploreEase...")
    print()

    graph = build_graph()

    query = """
    I have 4 days and want a peaceful mountain
    trip with my girlfriend. My budget is low.
    I don't want extreme cold.
    """

    initial_state = {
        "query": query,
        "retry_count": 0
    }

    result = graph.invoke(initial_state)

    print("=" * 60)
    print("EXPLOREEASE")
    print("=" * 60)

    print()
    print(result["answer"])

    print()
    print("-" * 60)
    print("Groundedness:", result["grounded"])

    if not result["grounded"]:
        print()
        print("Groundedness explanation:")
        print(result["groundedness_explanation"])

    print()


if __name__ == "__main__":
    main()