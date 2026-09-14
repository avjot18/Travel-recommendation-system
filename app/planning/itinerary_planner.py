
from pydantic import BaseModel, Field

from app.destination.models import (
    DestinationProfile
)

from app.query.analyzer import (
    TravelProfile
)

from app.planning.activity_planner import (
    ActivityPlan
)


class ItineraryDay(BaseModel):

    day: int

    day_type: str

    activities: list[str] = Field(
        default_factory=list
    )

    notes: list[str] = Field(
        default_factory=list
    )


class ItineraryPlan(BaseModel):

    destination: str

    duration_days: int

    days: list[ItineraryDay] = Field(
        default_factory=list
    )


class ItineraryPlanner:

    def plan(
        self,
        travel_profile: TravelProfile,
        destination: DestinationProfile,
        activity_plan: ActivityPlan
    ) -> ItineraryPlan:

        duration = (
            travel_profile.duration_days
        )

        if not duration or duration <= 0:

            duration = (
                destination.ideal_duration_days[0]
                if destination.ideal_duration_days
                else 1
            )

        # -------------------------------------------------
        # Create empty itinerary days
        # -------------------------------------------------

        days = [
            ItineraryDay(
                day=day_number,
                day_type="flexible"
            )
            for day_number in range(
                1,
                duration + 1
            )
        ]

        # -------------------------------------------------
        # Only use high and medium priority activities
        #
        # Low-priority activities are not automatically
        # added just to fill empty days.
        # -------------------------------------------------

        selected_activities = [
            activity
            for activity
            in activity_plan.activities
            if activity.priority
            in {"high", "medium"}
        ]

        # -------------------------------------------------
        # Limit activities to available days
        #
        # We currently don't know exact activity
        # durations, so one planned activity per day
        # keeps the itinerary conservative.
        # -------------------------------------------------

        selected_activities = (
            selected_activities[:duration]
        )

        # -------------------------------------------------
        # Distribute suitable activities
        # -------------------------------------------------

        for index, activity in enumerate(
            selected_activities
        ):

            days[index].activities.append(
                activity.name
            )

            days[index].day_type = (
                "activity"
            )

        # -------------------------------------------------
        # Add notes for each day
        # -------------------------------------------------

        for day in days:

            if day.day_type == "activity":

                day.notes.append(
                    "Activity selection is based "
                    "on your travel preferences."
                )

                day.notes.append(
                    "Exact activity duration and "
                    "travel time require live data."
                )

            else:

                day.notes.append(
                    "Keep this day flexible for "
                    "rest, local exploration, or "
                    "activities resolved through "
                    "live travel data."
                )

        return ItineraryPlan(
            destination=destination.name,
            duration_days=duration,
            days=days
        )

