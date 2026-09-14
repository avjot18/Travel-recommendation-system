from app.destination.repository import (
    DestinationRepository
)


DATA_PATH = (
    "data/"
    "india_travel_knowledge_base_v2_fully_populated.json"
)


def main():

    repository = DestinationRepository(
        DATA_PATH
    )

    destinations = (
        repository.get_all_destinations()
    )

    attractions = (
        repository.get_all_attractions()
    )

    print(
        f"Destinations: {len(destinations)}"
    )

    print(
        f"Attractions: {len(attractions)}"
    )

    print("\nFIRST DESTINATION")
    print("=================")

    destination = destinations[0]

    print(
        destination.model_dump()
    )

    print("\nATTRACTIONS FOR FIRST DESTINATION")
    print("=================================")

    linked_attractions = (
        repository.get_attractions_for_destination(
            destination.destination_id
        )
    )

    print(
        f"Linked attractions: "
        f"{len(linked_attractions)}"
    )

    for attraction in linked_attractions[:5]:

        print(
            "-",
            attraction.name
        )

    print("\nUNRESOLVED ATTRACTIONS")
    print("======================")

    unresolved = [
        attraction
        for attraction in attractions
        if attraction.destination_id
        == "resolve_via_live_place_search"
    ]

    print(
        f"Unresolved: {len(unresolved)}"
    )


if __name__ == "__main__":
    main()