 
import json

from app.destination.builder import (
    DestinationProfileBuilder
)

from app.planning.stay_area_planner import (
    StayAreaRecommender
)

from app.query.analyzer import (
    QueryAnalyzer
)


DATA_PATH = (
    "data/"
    "india_travel_knowledge_base_v2_fully_populated.json"
)


def main():

    # -------------------------------------------------
    # Load dataset
    # -------------------------------------------------

    with open(
        DATA_PATH,
        "r",
        encoding="utf-8"
    ) as file:

        data = json.load(file)

    # -------------------------------------------------
    # Build destination
    # -------------------------------------------------

    builder = (
        DestinationProfileBuilder()
    )

    manali_data = next(
        destination
        for destination
        in data["destinations"]
        if destination["name"] == "Manali"
    )

    destination = (
        builder.build_destination(
            manali_data
        )
    )

    # -------------------------------------------------
    # Analyze query
    # -------------------------------------------------

    query = (
        "I have 4 days and want a "
        "peaceful mountain trip with "
        "my girlfriend. My budget is low."
    )

    analyzer = QueryAnalyzer()

    travel_profile = (
        analyzer.analyze(query)
    )

    # -------------------------------------------------
    # Recommend stay areas
    # -------------------------------------------------

    recommender = (
        StayAreaRecommender()
    )

    plan = recommender.recommend(
        travel_profile,
        destination
    )

    # -------------------------------------------------
    # Display result
    # -------------------------------------------------

    print("\nSTAY AREA PLAN")
    print("==============")

    print(
        "Destination:",
        plan.destination
    )

    print(
        "Status:",
        plan.status
    )

    print(
        "\nRecommendations:"
    )

    if not plan.recommendations:

        print(
            "- No stay-area recommendations available."
        )

    else:

        for recommendation in plan.recommendations:

            print(
                f"- {recommendation.area}"
            )

            print(
                f"  Priority: "
                f"{recommendation.priority}"
            )

            for reason in recommendation.reasons:

                print(
                    f"  Reason: {reason}"
                )

    print(
        "\nLimitations:"
    )

    for limitation in plan.limitations:

        print(
            f"- {limitation}"
        )


if __name__ == "__main__":
    main()
 
