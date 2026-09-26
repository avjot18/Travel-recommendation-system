from pydantic import BaseModel, Field


class ActivityProfile(BaseModel):
    name: str
    description: str | None = None
    category: str | None = None
    best_seasons: list[str] = Field(default_factory=list)


class AttractionProfile(BaseModel):
    name: str
    description: str | None = None
    search_tags: list[str] = Field(default_factory=list)
    destination_id: str | None = None
    notes: str | None = None
    data_quality: str | None = None
    verification_status: str | None = None


class StayAreaProfile(BaseModel):
    name: str
    description: str | None = None
    suitable_for: list[str] = Field(default_factory=list)
    budget_tier: str | None = None


class DestinationProfile(BaseModel):
    destination_id: str
    name: str

    state_or_ut: str | None = None
    region: str | None = None
    description: str | None = None

    travel_styles: list[str] = Field(default_factory=list)
    best_for: list[str] = Field(default_factory=list)
    traveler_types: list[str] = Field(default_factory=list)

    pace: list[str] = Field(default_factory=list)
    crowd_level: str | None = None

    best_months: list[str] = Field(default_factory=list)
    season_profile: dict | None = None

    ideal_duration_days: list[int] = Field(default_factory=list)
    budget_tier: str | None = None

    activities: list[ActivityProfile] = Field(default_factory=list)
    attractions: list[AttractionProfile] = Field(default_factory=list)

    food_highlights: list[str] = Field(default_factory=list)

    stay_areas: list[StayAreaProfile] = Field(default_factory=list)

    transport: dict | None = None

    pros: list[str] = Field(default_factory=list)
    cons: list[str] = Field(default_factory=list)

    notes: str | None = None

    data_quality: str | None = None
    verification_status: str | None = None

    source_metadata: list[dict] = Field(default_factory=list)