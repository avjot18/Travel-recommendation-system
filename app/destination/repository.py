import json
from pathlib import Path

from app.destination.builder import (
    DestinationProfileBuilder
)


class DestinationRepository:

    def __init__(self, file_path: str):

        self.file_path = Path(file_path)

        self.builder = (
            DestinationProfileBuilder()
        )

        self.destinations = {}
        self.attractions = []

        self._load()

    def _load(self):

        with self.file_path.open(
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

        for destination in data.get(
            "destinations",
            []
        ):

            profile = (
                self.builder.build_destination(
                    destination
                )
            )

            self.destinations[
                profile.destination_id
            ] = profile

        for attraction in data.get(
            "attractions",
            []
        ):

            profile = (
                self.builder.build_attraction(
                    attraction
                )
            )

            self.attractions.append(
                profile
            )

    def get_destination(
        self,
        destination_id: str
    ):

        return self.destinations.get(
            destination_id
        )

    def get_all_destinations(self):

        return list(
            self.destinations.values()
        )

    def get_attractions_for_destination(
        self,
        destination_id: str
    ):

        return [
            attraction
            for attraction in self.attractions
            if attraction.destination_id
            == destination_id
        ]

    def get_all_attractions(self):

        return self.attractions