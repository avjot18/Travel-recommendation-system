import json

from app.destination.builder import (
    DestinationProfileBuilder
)

from app.planning.activity_planner import (
    ActivityPlanner
)

from app.query.analyzer import (
    QueryAnalyzer
)


DATA_PATH = (
    "data/"
    "india_travel_knowledge_base_v2_fully_populated.json"
)


def main():

    # ---------------------------------------------
    # Load dataset
    # ---------------------------------------------

    with open(
        DATA_PATH,
        "r",
        encoding="utf-8"
    ) as file:

        data = json.load(file)

    # ---------------------------------------------
    # Build destination
    # ---------------------------------------------

    builder = (
        DestinationProfileBuilder()
    )

    manali_data = next(
        destination
        for destination
        in data["destinations"]
        if destination["name"]
        == "Manali"
    )

    destination = (
        builder.build_destination(
            manali_data
        )
    )

    # ---------------------------------------------
    # Analyze user query
    # ---------------------------------------------

    query = (
        "I have 4 days and want a "
        "peaceful mountain trip with "
        "my girlfriend. I like photography."
    )

    analyzer = QueryAnalyzer()

    travel_profile = (
        analyzer.analyze(query)
    )

    # ---------------------------------------------
    # Plan activities
    # ---------------------------------------------

    planner = ActivityPlanner()

    activity_plan = planner.plan(
        travel_profile,
        destination
    )

    # ---------------------------------------------
    # Display
    # ---------------------------------------------

    print("\nTRAVEL PROFILE")
    print("==============")

    print(
        travel_profile.model_dump()
    )

    print("\nACTIVITY PLAN")
    print("=============")

    print(
        "Destination:",
        activity_plan.destination
    )

    for activity in (
        activity_plan.activities
    ):

        print(
            f"\n{activity.name}"
        )

        print(
            "Priority:",
            activity.priority
        )

        print(
            "Score:",
            activity.match_score
        )

        print(
            "Reasons:",
            activity.reasons
        )


if __name__ == "__main__":
    main()