import re
from pydantic import BaseModel


class TravelProfile(BaseModel):
    intent: str
    trip_type: str | None
    location: str | None
    duration_days: int | None
    budget_range: str | None
    season: str | None

    travelers: list[str]
    travel_styles: list[str]
    interests: list[str]
    activities: list[str]

    pace: str | None
    preferred_region: str | None

    must_have_activities: list[str]
    avoids: list[str]


class QueryAnalyzer:

    def analyze(self, query: str):

        text = query.lower()

        # -------------------------
        # Intent
        # -------------------------

        intent = "destination_recommendation"

        if any(
            word in text
            for word in ["compare", "comparison", "vs", "versus"]
        ):
            intent = "destination_comparison"

        # -------------------------
        # Duration
        # -------------------------

        duration_days = None

        duration_match = re.search(
            r"(\d+)\s*(?:day|days|day's)",
            text
        )

        if duration_match:
            duration_days = int(duration_match.group(1))

                # -------------------------
        # Budget
        # -------------------------

        budget_range = None

        if (
            re.search(r"\blow\b", text)
            and re.search(r"\bbudget\b", text)
        ) or any(
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
            budget_range = "low"

        elif any(
            phrase in text
            for phrase in [
                "mid range",
                "mid-range",
                "moderate budget",
                "medium budget"
            ]
        ):
            budget_range = "mid-range"

        elif any(
            phrase in text
            for phrase in [
                "luxury",
                "high budget",
                "expensive",
                "premium"
            ]
        ):
            budget_range = "luxury"

        # -------------------------
        # Travelers
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
        # Location
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

        elif any(
            word in text
            for word in [
                "beach",
                "beaches",
                "coast",
                "coastal"
            ]
        ):
            location = "beach"

        elif any(
            word in text
            for word in [
                "desert"
            ]
        ):
            location = "desert"

        # -------------------------
        # Trip Type
        # -------------------------

        trip_type = None

        if any(
            word in text
            for word in [
                "romantic",
                "romantic trip",
                "romantic getaway",
                "honeymoon"
            ]
        ):
            trip_type = "romantic"

        elif any(
            word in text
            for word in [
                "weekend",
                "weekend trip"
            ]
        ):
            trip_type = "weekend"

        elif any(
            word in text
            for word in [
                "adventure",
                "adventurous"
            ]
        ):
            trip_type = "adventure"

        elif any(
            word in text
            for word in [
                "spiritual",
                "pilgrimage"
            ]
        ):
            trip_type = "spiritual"

        elif any(
            word in text
            for word in [
                "wellness",
                "wellness trip"
            ]
        ):
            trip_type = "wellness"

        # -------------------------
        # Travel Styles
        # -------------------------

        travel_styles = []

        style_keywords = {
            "romantic": [
                "romantic",
                "romance",
                "honeymoon"
            ],
            "peaceful": [
                "peaceful",
                "peace",
                "quiet",
                "calm",
                "relaxing",
                "relaxed",
                "serene"
            ],
            "scenic": [
                "scenic",
                "beautiful views",
                "landscape",
                "photography"
            ],
            "adventure": [
                "adventure",
                "adventurous"
            ],
            "cultural": [
                "cultural",
                "culture",
                "heritage"
            ],
            "spiritual": [
                "spiritual",
                "spirituality",
                "pilgrimage"
            ],
            "wellness": [
                "wellness",
                "yoga",
                "meditation"
            ]
        }

        for style, keywords in style_keywords.items():

            if any(
                keyword in text
                for keyword in keywords
            ):
                travel_styles.append(style)

        # -------------------------
        # Season
        # -------------------------

        season = None

        if any(
            word in text
            for word in [
                "summer",
                "summertime"
            ]
        ):
            season = "summer"

        elif any(
            word in text
            for word in [
                "winter",
                "winters"
            ]
        ):
            season = "winter"

        elif any(
            word in text
            for word in [
                "monsoon",
                "rainy season",
                "rainy"
            ]
        ):
            season = "monsoon"

        elif any(
            word in text
            for word in [
                "spring"
            ]
        ):
            season = "spring"

        elif any(
            word in text
            for word in [
                "autumn",
                "fall"
            ]
        ):
            season = "autumn"

        # -------------------------
        # Pace
        # -------------------------

        pace = None

        if any(
            phrase in text
            for phrase in [
                "relaxed",
                "slow paced",
                "slow-paced",
                "not hectic",
                "easy pace",
                "take it easy"
            ]
        ):
            pace = "relaxed"

        elif any(
            phrase in text
            for phrase in [
                "fast paced",
                "fast-paced",
                "packed itinerary",
                "hectic"
            ]
        ):
            pace = "fast"

        # -------------------------
        # Activities
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
            ],
            "sightseeing": [
                "sightseeing",
                "sight seeing"
            ]
        }

        for activity, keywords in activity_keywords.items():

            if any(
                keyword in text
                for keyword in keywords
            ):
                activities.append(activity)

        # -------------------------
        # Interests
        # -------------------------

        interests = []

        interest_keywords = {
            "food": [
                "food",
                "local food",
                "cuisine"
            ],
            "nature": [
                "nature",
                "wildlife",
                "forests"
            ],
            "photography": [
                "photography",
                "photos"
            ],
            "culture": [
                "culture",
                "cultural",
                "heritage"
            ],
            "snow": [
                "snow",
                "snowy"
            ]
        }

        for interest, keywords in interest_keywords.items():

            if any(
                keyword in text
                for keyword in keywords
            ):
                interests.append(interest)

        # -------------------------
        # Avoidances
        # -------------------------

        avoids = []

        if any(
            phrase in text
            for phrase in [
                "don't want extreme cold",
                "do not want extreme cold",
                "avoid extreme cold",
                "no extreme cold"
            ]
        ):
            avoids.append("extreme_cold")

        if any(
            phrase in text
            for phrase in [
                "don't want crowds",
                "do not want crowds",
                "avoid crowds",
                "not crowded"
            ]
        ):
            avoids.append("crowds")

        if any(
            phrase in text
            for phrase in [
                "don't want a hectic trip",
                "do not want a hectic trip",
                "avoid hectic"
            ]
        ):
            avoids.append("hectic")

        # -------------------------
        # Must-have activities
        # -------------------------

        must_have_activities = []

        if any(
            phrase in text
            for phrase in [
                "must have",
                "must-have",
                "want to do",
                "want activities",
                "interested in"
            ]
        ):
            must_have_activities = activities.copy()

        # -------------------------
        # Preferred region
        # -------------------------

        preferred_region = None

        regions = [
            "north india",
            "south india",
            "east india",
            "west india",
            "northeast india"
        ]

        for region in regions:

            if region in text:
                preferred_region = region
                break

        return TravelProfile(
            intent=intent,
            trip_type=trip_type,
            location=location,
            duration_days=duration_days,
            budget_range=budget_range,
            season=season,
            travelers=travelers,
            travel_styles=travel_styles,
            interests=interests,
            activities=activities,
            pace=pace,
            preferred_region=preferred_region,
            must_have_activities=must_have_activities,
            avoids=avoids
        )