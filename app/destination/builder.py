from app.destination.models import (
    DestinationProfile,
    AttractionProfile
)

from app.destination.normalizer import (
    DestinationNormalizer
)


class DestinationProfileBuilder:

    def __init__(self):

        self.normalizer = (
            DestinationNormalizer()
        )

    def build_destination(
        self,
        destination: dict
    ) -> DestinationProfile:

        duration = (
            self.normalizer.normalize_duration(
                destination.get(
                    "ideal_duration_days"
                )
            )
        )

        return DestinationProfile(

            destination_id=destination.get(
                "destination_id"
            ),

            name=destination.get(
                "name"
            ),

            state_or_ut=destination.get(
                "state_or_ut"
            ),

            region=destination.get(
                "region"
            ),

            description=destination.get(
                "description"
            ),

            travel_styles=destination.get(
                "travel_styles",
                []
            ),

            best_for=destination.get(
                "best_for",
                []
            ),

            best_months=destination.get(
                "best_months",
                []
            ),

            ideal_duration_days=duration,

            budget_tier=destination.get(
                "budget_tier"
            ),

            activities=destination.get(
                "activities",
                []
            ),

            food_highlights=destination.get(
                "food_highlights",
                []
            ),

            pros=destination.get(
                "pros",
                []
            ),

            cons=destination.get(
                "cons",
                []
            ),

            notes=destination.get(
                "notes"
            ),

            data_quality=destination.get(
                "data_quality"
            ),

            verification_status=destination.get(
                "verification_status"
            )
        )

    def build_attraction(
        self,
        attraction: dict
    ) -> AttractionProfile:

        return AttractionProfile(

            name=attraction.get(
                "name"
            ),

            description=attraction.get(
                "description"
            ),

            search_tags=attraction.get(
                "search_tags",
                []
            ),

            destination_id=attraction.get(
                "destination_id"
            ),

            notes=attraction.get(
                "notes"
            ),

            data_quality=attraction.get(
                "data_quality"
            ),

            verification_status=attraction.get(
                "verification_status"
            )
        )