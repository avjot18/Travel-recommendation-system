 
from pydantic import BaseModel, Field

from app.destination.models import (
    DestinationProfile
)

from app.query.analyzer import (
    TravelProfile
)


class StayAreaRecommendation(BaseModel):

    area: str

    priority: str

    reasons: list[str] = Field(
        default_factory=list
    )


class StayAreaPlan(BaseModel):

    destination: str

    recommendations: list[StayAreaRecommendation] = Field(
        default_factory=list
    )

    status: str

    limitations: list[str] = Field(
        default_factory=list
    )


class StayAreaRecommender:

    def recommend(
        self,
        travel_profile: TravelProfile,
        destination: DestinationProfile
    ) -> StayAreaPlan:

        # The current knowledge base does not contain
        # structured stay-area information.

        return StayAreaPlan(

            destination=destination.name,

            recommendations=[],

            status="unavailable",

            limitations=[
                (
                    "The current destination knowledge "
                    "does not contain structured stay-area data."
                ),
                (
                    "Area-level recommendations require "
                    "additional static knowledge or live place data."
                )
            ]
        )
 
