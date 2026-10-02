from pydantic import BaseModel, Field


class TravelProfile(BaseModel):
    intent: str

    trip_type: str | None = None

    location: str | None = None

    duration_days: int | None = None

    budget_range: str | None = None

    season: str | None = None

    travelers: list[str] = Field(
        default_factory=list
    )

    travel_styles: list[str] = Field(
        default_factory=list
    )

    interests: list[str] = Field(
        default_factory=list
    )

    activities: list[str] = Field(
        default_factory=list
    )

    pace: str | None = None

    preferred_region: str | None = None

    must_have_activities: list[str] = Field(
        default_factory=list
    )

    avoids: list[str] = Field(
        default_factory=list
    )

    needs_live_weather: bool = False