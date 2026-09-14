 
import json

from app.destination.builder import (
    DestinationProfileBuilder
)

from app.planning.activity_planner import (
    ActivityPlanner
)

from app.planning.itinerary_planner import (
    ItineraryPlanner
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
        if destination["name"]
        == "Manali"
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
        "my girlfriend. I like photography."
    )

    analyzer = QueryAnalyzer()

    travel_profile = (
        analyzer.analyze(query)
    )

    # -------------------------------------------------
    # Activity planning
    # -------------------------------------------------

    activity_planner = (
        ActivityPlanner()
    )

    activity_plan = (
        activity_planner.plan(
            travel_profile,
            destination
        )
    )

    # -------------------------------------------------
    # Itinerary planning
    # -------------------------------------------------

    itinerary_planner = (
        ItineraryPlanner()
    )

    itinerary = (
        itinerary_planner.plan(
            travel_profile,
            destination,
            activity_plan
        )
    )

    # -------------------------------------------------
    # Display result
    # -------------------------------------------------

    print("\nITINERARY")
    print("=========")

    print(
        "Destination:",
        itinerary.destination
    )

    print(
        "Duration:",
        itinerary.duration_days,
        "days"
    )

    for day in itinerary.days:

        print(
            f"\nDay {day.day}"
        )

        if day.activities:

            print(
                "Activities:"
            )

            for activity in (
                day.activities
            ):

                print(
                    "-",
                    activity
                )

        print(
            "Notes:"
        )

        for note in day.notes:

            print(
                "-",
                note
            )


if __name__ == "__main__":
    main()
 
