from pydantic import BaseModel, Field


class ExtractedActivity(BaseModel):
    name: str
    description: str | None = None
    category: str | None = None
    best_seasons: list[str] = Field(
        default_factory=list
    )


class ExtractedAttraction(BaseModel):
    name: str
    description: str | None = None
    search_tags: list[str] = Field(
        default_factory=list
    )


class ExtractedFood(BaseModel):
    name: str
    description: str | None = None


class ExtractedStayArea(BaseModel):
    name: str
    description: str | None = None
    suitable_for: list[str] = Field(
        default_factory=list
    )
    budget_tier: str | None = None


class ExtractedTransport(BaseModel):
    type: str | None = None
    name: str | None = None


class ExtractedSeason(BaseModel):
    month: str
    temperature: str | None = None


class ExtractedDestinationData(BaseModel):

    description: str | None = None

    traveler_types: list[str] = Field(
        default_factory=list
    )

    pace: list[str] | None = None

    crowd_level: str | None = None

    best_months: list[str] = Field(
        default_factory=list
    )

    season_profile: list[ExtractedSeason] = Field(
        default_factory=list
    )

    activities: list[ExtractedActivity] = Field(
        default_factory=list
    )

    attractions: list[ExtractedAttraction] = Field(
        default_factory=list
    )

    food_highlights: list[ExtractedFood] = Field(
        default_factory=list
    )

    stay_areas: list[ExtractedStayArea] = Field(
        default_factory=list
    )

    transport: list[ExtractedTransport] = Field(
        default_factory=list
    )

    pros: list[str] | None = None

    cons: list[str] | None = None

    notes: str | None = None