 
from pydantic import BaseModel, Field

from app.destination.models import (
    DestinationProfile
)

from app.query.analyzer import (
    TravelProfile
)

from app.planning.activity_knowledge import (
    ActivityKnowledge
)


class PlannedActivity(BaseModel):

    name: str

    priority: str

    match_score: float

    reasons: list[str] = Field(
        default_factory=list
    )


class ActivityPlan(BaseModel):

    destination: str

    activities: list[PlannedActivity] = Field(
        default_factory=list
    )


class ActivityPlanner:

    def plan(
        self,
        travel_profile: TravelProfile,
        destination: DestinationProfile
    ) -> ActivityPlan:

        planned_activities = []

        for activity in destination.activities:

            score = 0.0
            reasons = []

            activity_lower = (
                activity.lower()
            )

            # ---------------------------------------------
            # Direct activity match
            # ---------------------------------------------

            for requested_activity in (
                travel_profile.activities
            ):

                requested_lower = (
                    requested_activity.lower()
                )

                if (
                    requested_lower
                    in activity_lower
                    or activity_lower
                    in requested_lower
                ):

                    score += 1.0

                    reasons.append(
                        "Matches your requested activity."
                    )

            # ---------------------------------------------
            # Interest compatibility
            # ---------------------------------------------

            for interest in (
                travel_profile.interests
            ):

                interest_lower = (
                    interest.lower()
                )

                if (
                    interest_lower
                    in activity_lower
                ):

                    score += 0.5

                    reasons.append(
                        "Matches one of your interests."
                    )

            # ---------------------------------------------
            # Travel-style compatibility
            # ---------------------------------------------

            for style in (
                travel_profile.travel_styles
            ):

                compatible_activities = (
                    ActivityKnowledge.activities_for_style(
                        style
                    )
                )

                if activity_lower in (
                    compatible_activities
                ):

                    score += 0.5

                    reasons.append(
                        f"Fits your {style} "
                        "travel style."
                    )

            # ---------------------------------------------
            # Avoided activities
            # ---------------------------------------------

            avoided = False

            for avoid in travel_profile.avoids:

                if (
                    avoid.lower()
                    in activity_lower
                ):

                    avoided = True

                    reasons.append(
                        "Conflicts with an "
                        "explicit avoidance."
                    )

            if avoided:
                continue

            # ---------------------------------------------
            # Default destination activity
            # ---------------------------------------------

            if score == 0:

                score = 0.2

                reasons.append(
                    "Available at the destination."
                )

            # ---------------------------------------------
            # Priority
            # ---------------------------------------------

            if score >= 1.0:

                priority = "high"

            elif score >= 0.5:

                priority = "medium"

            else:

                priority = "low"

            planned_activities.append(
                PlannedActivity(
                    name=activity,
                    priority=priority,
                    match_score=round(
                        score,
                        2
                    ),
                    reasons=reasons
                )
            )

        # ---------------------------------------------
        # Highest match first
        # ---------------------------------------------

        planned_activities.sort(
            key=lambda activity: (
                activity.match_score
            ),
            reverse=True
        )

        return ActivityPlan(
            destination=destination.name,
            activities=planned_activities
        )
 
