from dataclasses import dataclass

import requests


@dataclass
class LocationData:
    name: str
    latitude: float
    longitude: float
    country: str | None = None
    admin1: str | None = None
    timezone: str | None = None


class GeocodingTool:

    BASE_URL = "https://geocoding-api.open-meteo.com/v1/search"

    def __init__(self, timeout: int = 10):
        self.timeout = timeout

    def search(
        self,
        query: str,
        state: str | None = None,
        country_code: str = "IN",
    ) -> LocationData | None:

        if not query.strip():
            raise ValueError(
                "Location query cannot be empty."
            )

        # Add state information to reduce
        # ambiguity between locations with
        # the same name.
        search_query = query

        if state:
            search_query = (
                f"{query}, {state}, India"
            )

        params = {
            "name": search_query,
            "count": 10,
            "language": "en",
            "format": "json",
        }

        response = requests.get(
            self.BASE_URL,
            params=params,
            timeout=self.timeout,
        )

        response.raise_for_status()

        data = response.json()

        results = data.get("results", [])

        if not results:
            return None

        # Prefer the requested country.
        indian_results = [
            result
            for result in results
            if result.get("country_code")
            == country_code
        ]

        if indian_results:
            results = indian_results

        # Prefer the requested state.
        if state:
            state_matches = [
                result
                for result in results
                if state.lower()
                in result.get(
                    "admin1",
                    "",
                ).lower()
            ]

            if state_matches:
                results = state_matches

        result = results[0]

        return LocationData(
            name=result.get(
                "name",
                query,
            ),
            latitude=result["latitude"],
            longitude=result["longitude"],
            country=result.get(
                "country"
            ),
            admin1=result.get(
                "admin1"
            ),
            timezone=result.get(
                "timezone"
            ),
        )


if __name__ == "__main__":

    tool = GeocodingTool()

    location = tool.search(
        "Manali",
        state="Himachal Pradesh",
    )

    print("LOCATION")
    print("=" * 40)

    if location is None:

        print("Location not found.")

    else:

        print(
            "Name:",
            location.name,
        )

        print(
            "Latitude:",
            location.latitude,
        )

        print(
            "Longitude:",
            location.longitude,
        )

        print(
            "Country:",
            location.country,
        )

        print(
            "State:",
            location.admin1,
        )

        print(
            "Timezone:",
            location.timezone,
        )