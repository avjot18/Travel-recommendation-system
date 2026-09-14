from pydantic import BaseModel, Field


class DestinationProfile(BaseModel):

    destination_id: str
    name: str

    state_or_ut: str | None = None
    region: str | None = None

    description: str | None = None

    travel_styles: list[str] = Field(
        default_factory=list
    )

    best_for: list[str] = Field(
        default_factory=list
    )

    best_months: list[str] = Field(
        default_factory=list
    )

    ideal_duration_days: list[int] = Field(
        default_factory=list
    )

    budget_tier: str | None = None

    activities: list[str] = Field(
        default_factory=list
    )

    food_highlights: list[str] = Field(
        default_factory=list
    )

    pros: list[str] = Field(
        default_factory=list
    )

    cons: list[str] = Field(
        default_factory=list
    )

    notes: str | None = None

    data_quality: str | None = None
    verification_status: str | None = None


class AttractionProfile(BaseModel):

    name: str

    description: str | None = None

    search_tags: list[str] = Field(
        default_factory=list
    )

    destination_id: str | None = None

    notes: str | None = None

    data_quality: str | None = None
    verification_status: str | None = None