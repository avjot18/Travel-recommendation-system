import json

from app.destination.builder import (
    DestinationProfileBuilder
)


DATA_PATH = (
    "data/"
    "india_travel_knowledge_base_v2_fully_populated.json"
)


def main():

    with open(
        DATA_PATH,
        "r",
        encoding="utf-8"
    ) as file:

        data = json.load(file)

    builder = DestinationProfileBuilder()

    destination = builder.build_destination(
        data["destinations"][0]
    )

    attraction = builder.build_attraction(
        data["attractions"][0]
    )

    print("\nDESTINATION PROFILE")
    print("===================")
    print(destination.model_dump())

    print("\nATTRACTION PROFILE")
    print("==================")
    print(attraction.model_dump())


if __name__ == "__main__":
    main()