import re
from pydantic import BaseModel


class QueryAnalysis(BaseModel):
    intent: str
    location: str | None
    duration_days: int | None
    budget: str | None
    travelers: list[str]
    preferences: list[str]
    activities: list[str]
    constraints: list[str]


class QueryAnalyzer:

    def analyze(self, query: str):

        text = query.lower()

        # -------------------------
        # INTENT
        # -------------------------

        intent = "destination_recommendation"

        if any(
            word in text
            for word in [
                "compare",
                "comparison",
                "vs",
                "versus"
            ]
        ):
            intent = "destination_comparison"

        # -------------------------
        # DURATION
        # -------------------------

        duration_days = None

        duration_match = re.search(
            r"(\d+)\s*(?:day|days|day's)",
            text
        )

        if duration_match:
            duration_days = int(
                duration_match.group(1)
            )

        # -------------------------
        # BUDGET
        # -------------------------

        budget = None

        if any(
            phrase in text
            for phrase in [
                "low budget",
                "cheap",
                "budget friendly",
                "budget-friendly",
                "affordable",
                "cheap trip"
            ]
        ):
            budget = "low"

        elif any(
            phrase in text
            for phrase in [
                "mid range",
                "mid-range",
                "moderate budget",
                "medium budget"
            ]
        ):
            budget = "mid-range"

        elif any(
            phrase in text
            for phrase in [
                "luxury",
                "high budget",
                "expensive"
            ]
        ):
            budget = "luxury"

        # -------------------------
        # TRAVELERS
        # -------------------------

        travelers = []

        if any(
            phrase in text
            for phrase in [
                "girlfriend",
                "boyfriend",
                "couple",
                "couples",
                "romantic trip",
                "romantic getaway",
                "partner"
            ]
        ):
            travelers.append("couples")

        if any(
            phrase in text
            for phrase in [
                "family",
                "parents",
                "kids",
                "children"
            ]
        ):
            travelers.append("family")

        if any(
            phrase in text
            for phrase in [
                "solo",
                "alone",
                "myself"
            ]
        ):
            travelers.append("solo")

        if any(
            phrase in text
            for phrase in [
                "friends",
                "group of friends",
                "friend group"
            ]
        ):
            travelers.append("friends")

        # -------------------------
        # LOCATION
        # -------------------------

        location = None

        if any(
            word in text
            for word in [
                "mountain",
                "mountains",
                "hill",
                "hills"
            ]
        ):
            location = "mountains"

        # -------------------------
        # PREFERENCES
        # -------------------------

        preferences = []

        if any(
            word in text
            for word in [
                "peaceful",
                "peace",
                "quiet",
                "calm",
                "relaxing",
                "relaxed",
                "serene"
            ]
        ):
            preferences.append("peaceful")

        if any(
            word in text
            for word in [
                "scenic",
                "beautiful views",
                "landscape",
                "photography"
            ]
        ):
            preferences.append("scenic")

        if any(
            word in text
            for word in [
                "adventure",
                "adventurous"
            ]
        ):
            preferences.append("adventure")

        # -------------------------
        # ACTIVITIES
        # -------------------------

        activities = []

        activity_keywords = {
            "trekking": [
                "trek",
                "trekking",
                "hiking"
            ],
            "skiing": [
                "ski",
                "skiing"
            ],
            "rafting": [
                "rafting",
                "raft"
            ],
            "camping": [
                "camping",
                "camp"
            ],
            "photography": [
                "photography",
                "photograph",
                "photos"
            ],
            "yoga": [
                "yoga"
            ],
            "meditation": [
                "meditation"
            ]
        }

        for activity, keywords in activity_keywords.items():

            if any(
                keyword in text
                for keyword in keywords
            ):
                activities.append(activity)

        # -------------------------
        # CONSTRAINTS
        # -------------------------

        constraints = []

        if (
            "don't want extreme cold" in text
            or "do not want extreme cold" in text
            or "avoid extreme cold" in text
            or "no extreme cold" in text
        ):
            constraints.append(
                "avoid_extreme_cold"
            )

        return QueryAnalysis(
            intent=intent,
            location=location,
            duration_days=duration_days,
            budget=budget,
            travelers=travelers,
            preferences=preferences,
            activities=activities,
            constraints=constraints
        )