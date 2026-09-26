import json
from pathlib import Path

from app.destination.models import (
    ActivityProfile,
    AttractionProfile,
    StayAreaProfile,
    DestinationProfile,
)


STAGING_DIR = Path("data/staging")

DATASET_PATH = Path(
    "data/india_travel_knowledge_base_v2_fully_populated.json"
)


class KnowledgeBuilder:

    def __init__(
        self,
        dataset_path: Path = DATASET_PATH,
        staging_dir: Path = STAGING_DIR,
    ):
        self.dataset_path = dataset_path
        self.staging_dir = staging_dir

    # =========================================================
    # Dataset
    # =========================================================

    def load_dataset(self):
        with self.dataset_path.open(
            "r",
            encoding="utf-8",
        ) as file:
            return json.load(file)

    def find_destination(
        self,
        destinations,
        destination_id,
    ):
        for destination in destinations:
            if destination.get("destination_id") == destination_id:
                return destination

        return None

    # =========================================================
    # Staging
    # =========================================================

    def load_staging(
        self,
        destination_id,
    ):
        path = (
            self.staging_dir
            / destination_id
            / "validated.json"
        )

        if not path.exists():
            raise FileNotFoundError(
                f"Staging file not found: {path}"
            )

        with path.open(
            "r",
            encoding="utf-8",
        ) as file:
            return json.load(file)

    # =========================================================
    # Main builder
    # =========================================================

    def build_profile(
        self,
        existing_destination,
        staging_data,
    ):
        destination_id = existing_destination[
            "destination_id"
        ]

        blocks = staging_data.get(
            "blocks",
            [],
        )

        temperature_blocks = self._get_blocks(
            blocks,
            "temperature",
        )

        transport_blocks = self._get_blocks(
            blocks,
            "transport",
        )

        activities = self._build_activities(
            existing_destination.get(
                "activities",
                [],
            )
        )

        attractions = self._build_attractions(
            existing_destination.get(
                "attractions",
                [],
            )
        )

        stay_areas = self._build_stay_areas(
            existing_destination.get(
                "stay_areas",
                [],
            )
        )

        season_profile = self._build_season_profile(
            temperature_blocks
        )

        transport = self._build_transport(
            transport_blocks
        )

        source_metadata = self._build_source_metadata(
            staging_data
        )

        profile = DestinationProfile(
            destination_id=destination_id,

            name=existing_destination.get(
                "name",
                "",
            ),

            state_or_ut=existing_destination.get(
                "state_or_ut"
            ),

            region=existing_destination.get(
                "region"
            ),

            description=existing_destination.get(
                "description"
            ),

            travel_styles=existing_destination.get(
                "travel_styles",
                [],
            ),

            best_for=existing_destination.get(
                "best_for",
                [],
            ),

            traveler_types=existing_destination.get(
                "traveler_types",
                [],
            ),

            pace=existing_destination.get(
                "pace",
                [],
            ),

            crowd_level=existing_destination.get(
                "crowd_level"
            ),

            best_months=existing_destination.get(
                "best_months",
                [],
            ),

            season_profile=season_profile,

            ideal_duration_days=self._normalize_duration(
                existing_destination.get(
                    "ideal_duration_days"
                )
            ),

            budget_tier=existing_destination.get(
                "budget_tier"
            ),

            activities=activities,

            attractions=attractions,

            food_highlights=self._deduplicate_strings(
                existing_destination.get(
                    "food_highlights",
                    [],
                )
            ),

            stay_areas=stay_areas,

            transport=transport,

            pros=self._deduplicate_strings(
                existing_destination.get(
                    "pros",
                    [],
                )
            ),

            cons=self._deduplicate_strings(
                existing_destination.get(
                    "cons",
                    [],
                )
            ),

            notes=existing_destination.get(
                "notes"
            ),

            data_quality=existing_destination.get(
                "data_quality"
            ),

            verification_status=(
                "official_page_enriched"
            ),

            source_metadata=source_metadata,
        )

        return profile

    # =========================================================
    # Block helpers
    # =========================================================

    @staticmethod
    def _get_blocks(
        blocks,
        block_type,
    ):
        return [
            block
            for block in blocks
            if block.get("block_type") == block_type
        ]

    # =========================================================
    # Activities
    # =========================================================

    def _build_activities(
        self,
        existing_activities,
    ):
        activities = []

        for activity in existing_activities or []:

            if isinstance(activity, str):
                name = self._clean_text(activity)

                if name:
                    activities.append(
                        ActivityProfile(
                            name=name
                        )
                    )

            elif isinstance(activity, dict):
                name = self._clean_text(
                    activity.get("name")
                )

                if not name:
                    continue

                activities.append(
                    ActivityProfile(
                        name=name,
                        description=self._clean_optional_text(
                            activity.get("description")
                        ),
                        category=self._clean_optional_text(
                            activity.get("category")
                        ),
                        best_seasons=activity.get(
                            "best_seasons",
                            [],
                        ),
                    )
                )

        return self._deduplicate_activities(
            activities
        )

    # =========================================================
    # Attractions
    # =========================================================

    def _build_attractions(
        self,
        existing_attractions,
    ):
        attractions = []

        for attraction in existing_attractions or []:

            if isinstance(attraction, str):
                name = self._clean_text(
                    attraction
                )

                if name:
                    attractions.append(
                        AttractionProfile(
                            name=name
                        )
                    )

            elif isinstance(attraction, dict):
                name = self._clean_text(
                    attraction.get("name")
                )

                if not name:
                    continue

                attractions.append(
                    AttractionProfile(
                        name=name,
                        description=self._clean_optional_text(
                            attraction.get("description")
                        ),
                        search_tags=[
                            self._clean_text(tag)
                            for tag in attraction.get(
                                "search_tags",
                                [],
                            )
                            if self._clean_text(tag)
                        ],
                        destination_id=attraction.get(
                            "destination_id"
                        ),
                        notes=self._clean_optional_text(
                            attraction.get("notes")
                        ),
                        data_quality=attraction.get(
                            "data_quality"
                        ),
                        verification_status=attraction.get(
                            "verification_status"
                        ),
                    )
                )

        return self._deduplicate_attractions(
            attractions
        )

    # =========================================================
    # Season profile
    # =========================================================

    def _build_season_profile(
        self,
        temperature_blocks,
    ):
        season_profile = {}

        for block in temperature_blocks:

            content = block.get(
                "content",
                {}
            )

            month = content.get(
                "month"
            )

            if not month:
                continue

            month = self._clean_text(
                month
            ).lower()

            minimum = content.get(
                "minimum_celsius"
            )

            maximum = content.get(
                "maximum_celsius"
            )

            season_profile[month] = {
                "minimum_celsius": minimum,
                "maximum_celsius": maximum,
            }

        return season_profile or None

    # =========================================================
    # Transport
    # =========================================================

    def _build_transport(
        self,
        transport_blocks,
    ):
        transport = {}

        for block in transport_blocks:

            content = block.get(
                "content",
                {}
            )

            transport_type = self._clean_text(
                content.get("transport_type")
            )

            value = self._clean_text(
                content.get("value")
            )

            if not transport_type or not value:
                continue

            if transport_type not in transport:
                transport[transport_type] = []

            if value not in transport[transport_type]:
                transport[transport_type].append(
                    value
                )

        return transport

    # =========================================================
    # Stay areas
    # =========================================================

    def _build_stay_areas(
        self,
        stay_areas,
    ):
        result = []

        for area in stay_areas or []:

            if isinstance(area, str):

                name = self._clean_text(area)

                if name:
                    result.append(
                        StayAreaProfile(
                            name=name
                        )
                    )

            elif isinstance(area, dict):

                name = self._clean_text(
                    area.get("name")
                )

                if not name:
                    continue

                result.append(
                    StayAreaProfile(
                        name=name,
                        description=self._clean_optional_text(
                            area.get("description")
                        ),
                        suitable_for=[
                            self._clean_text(item)
                            for item in area.get(
                                "suitable_for",
                                [],
                            )
                            if self._clean_text(item)
                        ],
                        budget_tier=self._clean_optional_text(
                            area.get("budget_tier")
                        ),
                    )
                )

        return self._deduplicate_stay_areas(
            result
        )

    # =========================================================
    # Provenance
    # =========================================================

    def _build_source_metadata(
        self,
        staging_data,
    ):
        source_url = staging_data.get(
            "source_url"
        )

        if not source_url:
            return []

        blocks = staging_data.get(
            "blocks",
            []
        )

        sources = []

        for block in blocks:

            source = block.get(
                "source",
                {}
            )

            url = source.get(
                "source_url",
                source_url,
            )

            source_entry = {
                "source_name": source.get(
                    "source_name"
                ),
                "source_url": url,
                "retrieved_at": source.get(
                    "retrieved_at"
                ),
                "source_type": source.get(
                    "source_type"
                ),
            }

            if source_entry not in sources:
                sources.append(
                    source_entry
                )

        if not sources:
            sources.append(
                {
                    "source_name": None,
                    "source_url": source_url,
                    "retrieved_at": None,
                    "source_type": (
                        "official_tourism_page"
                    ),
                }
            )

        return sources

    # =========================================================
    # Duration
    # =========================================================

    @staticmethod
    def _normalize_duration(
        value
    ):
        if value is None:
            return []

        if isinstance(value, list):
            return [
                int(item)
                for item in value
                if isinstance(
                    item,
                    (int, float),
                )
            ]

        if isinstance(value, tuple):
            return [
                int(item)
                for item in value
                if isinstance(
                    item,
                    (int, float),
                )
            ]

        return []

    # =========================================================
    # Text cleaning
    # =========================================================

    @staticmethod
    def _clean_text(
        value
    ):
        if value is None:
            return ""

        text = str(value).strip()

        # Repair common UTF-8/Latin-1 mojibake.
        if any(
            marker in text
            for marker in (
                "â€“",
                "â€”",
                "â€™",
                "â€œ",
                "â€",
                "â€¦",
            )
        ):
            try:
                text = text.encode(
                    "latin1"
                ).decode(
                    "utf-8"
                )
            except (
                UnicodeEncodeError,
                UnicodeDecodeError,
            ):
                pass

        return " ".join(
            text.split()
        )

    @classmethod
    def _clean_optional_text(
        cls,
        value,
    ):
        cleaned = cls._clean_text(
            value
        )

        return cleaned or None

    # =========================================================
    # Deduplication
    # =========================================================

    @classmethod
    def _deduplicate_strings(
        cls,
        values,
    ):
        result = []
        seen = set()

        for value in values or []:

            cleaned = cls._clean_text(
                value
            )

            if not cleaned:
                continue

            key = cleaned.lower()

            if key in seen:
                continue

            seen.add(key)
            result.append(cleaned)

        return result

    @classmethod
    def _deduplicate_activities(
        cls,
        activities,
    ):
        result = []
        seen = set()

        for activity in activities:

            key = cls._clean_text(
                activity.name
            ).lower()

            if not key or key in seen:
                continue

            seen.add(key)
            result.append(activity)

        return result

    @classmethod
    def _deduplicate_attractions(
        cls,
        attractions,
    ):
        result = []
        seen = set()

        for attraction in attractions:

            key = cls._clean_text(
                attraction.name
            ).lower()

            if not key or key in seen:
                continue

            seen.add(key)
            result.append(attraction)

        return result

    @classmethod
    def _deduplicate_stay_areas(
        cls,
        stay_areas,
    ):
        result = []
        seen = set()

        for area in stay_areas:

            key = cls._clean_text(
                area.name
            ).lower()

            if not key or key in seen:
                continue

            seen.add(key)
            result.append(area)

        return result


# =============================================================
# Manual Manali test
# =============================================================

if __name__ == "__main__":

    builder = KnowledgeBuilder()

    dataset = builder.load_dataset()

    destinations = dataset.get(
        "destinations",
        [],
    )

    destination = builder.find_destination(
        destinations,
        "IN-HIMACHAL-PRADESH-MANALI",
    )

    if destination is None:
        raise ValueError(
            "Manali not found in dataset."
        )

    staging = builder.load_staging(
        "IN-HIMACHAL-PRADESH-MANALI"
    )

    profile = builder.build_profile(
        existing_destination=destination,
        staging_data=staging,
    )

    print("=" * 60)
    print("KNOWLEDGE BUILDER TEST")
    print("=" * 60)

    print(
        f"Destination: {profile.name}"
    )

    print(
        f"Destination ID: {profile.destination_id}"
    )

    print(
        f"Activities: {len(profile.activities)}"
    )

    print(
        f"Attractions: {len(profile.attractions)}"
    )

    print(
        f"Food: {len(profile.food_highlights)}"
    )

    print(
        f"Best months: {len(profile.best_months)}"
    )

    print(
        f"Season months: "
        f"{len(profile.season_profile or {})}"
    )

    print(
        f"Transport types: "
        f"{len(profile.transport or {})}"
    )

    print(
        f"Sources: {len(profile.source_metadata)}"
    )

    print("\nActivities:")

    for activity in profile.activities:
        print(
            f"  - {activity.name}"
        )

    print("\nSeason profile:")

    for month, data in (
        profile.season_profile or {}
    ).items():

        print(
            f"  - {month}: "
            f"{data['minimum_celsius']}°C "
            f"to "
            f"{data['maximum_celsius']}°C"
        )

    print("\nTransport:")

    for transport_type, values in (
        profile.transport or {}
    ).items():

        print(
            f"  - {transport_type}:"
        )

        for value in values:
            print(
                f"      {value}"
            )

    print("\nSource metadata:")

    for source in profile.source_metadata:
        print(
            f"  - {source['source_url']}"
        )

    print("\nProfile validation:")

    print(
        profile.model_dump_json(
            indent=2
        )
    )