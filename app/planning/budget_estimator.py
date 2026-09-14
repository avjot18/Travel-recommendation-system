
from pydantic import BaseModel, Field

from app.destination.models import (
    DestinationProfile
)

from app.query.analyzer import (
    TravelProfile
)

from app.planning.budget_knowledge import (
    BudgetKnowledge
)


class BudgetItem(BaseModel):

    category: str
    amount: float | None = None
    status: str
    basis: str


class BudgetPlan(BaseModel):

    destination: str
    duration_days: int
    budget_tier: str | None = None

    items: list[BudgetItem] = Field(
        default_factory=list
    )

    total: float | None = None
    total_status: str

    assumptions: list[str] = Field(
        default_factory=list
    )


class BudgetEstimator:

    def estimate(
        self,
        travel_profile: TravelProfile,
        destination: DestinationProfile
    ) -> BudgetPlan:

        # -------------------------------------------------
        # Duration
        # -------------------------------------------------

        duration = travel_profile.duration_days

        if not duration or duration <= 0:

            duration = (
                destination.ideal_duration_days[0]
                if destination.ideal_duration_days
                else 1
            )

        # -------------------------------------------------
        # Budget tier
        # -------------------------------------------------

        budget_tier = (
            travel_profile.budget_range
            or destination.budget_tier
        )

        # -------------------------------------------------
        # Budget assumptions
        # -------------------------------------------------

        budget_assumptions = (
            BudgetKnowledge.get_assumptions(
                budget_tier
            )
        )

        # Human-readable explanations
        assumptions = []

        items = []

        # -------------------------------------------------
        # Accommodation
        # -------------------------------------------------

        accommodation = (
            budget_assumptions.get(
                "accommodation_per_day"
            )
        )

        if accommodation is not None:

            amount = (
                accommodation * duration
            )

            items.append(
                BudgetItem(
                    category="accommodation",
                    amount=amount,
                    status="estimated",
                    basis=(
                        "Generic budget-tier planning "
                        "assumption multiplied by trip duration."
                    )
                )
            )

        else:

            items.append(
                BudgetItem(
                    category="accommodation",
                    amount=None,
                    status="unavailable",
                    basis=(
                        "No accommodation pricing "
                        "assumption is available."
                    )
                )
            )

        # -------------------------------------------------
        # Food
        # -------------------------------------------------

        food = (
            budget_assumptions.get(
                "food_per_day"
            )
        )

        if food is not None:

            amount = food * duration

            items.append(
                BudgetItem(
                    category="food",
                    amount=amount,
                    status="estimated",
                    basis=(
                        "Generic budget-tier daily "
                        "food assumption."
                    )
                )
            )

        else:

            items.append(
                BudgetItem(
                    category="food",
                    amount=None,
                    status="unavailable",
                    basis=(
                        "No food pricing assumption "
                        "is available."
                    )
                )
            )

        # -------------------------------------------------
        # Local transport
        # -------------------------------------------------

        local_transport = (
            budget_assumptions.get(
                "local_transport_per_day"
            )
        )

        if local_transport is not None:

            amount = (
                local_transport * duration
            )

            items.append(
                BudgetItem(
                    category="local_transport",
                    amount=amount,
                    status="estimated",
                    basis=(
                        "Generic budget-tier daily "
                        "local transport assumption."
                    )
                )
            )

        else:

            items.append(
                BudgetItem(
                    category="local_transport",
                    amount=None,
                    status="unavailable",
                    basis=(
                        "No local transport pricing "
                        "assumption is available."
                    )
                )
            )

        # -------------------------------------------------
        # Miscellaneous
        # -------------------------------------------------

        miscellaneous = (
            budget_assumptions.get(
                "miscellaneous_per_day"
            )
        )

        if miscellaneous is not None:

            amount = (
                miscellaneous * duration
            )

            items.append(
                BudgetItem(
                    category="miscellaneous",
                    amount=amount,
                    status="estimated",
                    basis=(
                        "Generic budget-tier daily "
                        "miscellaneous-cost assumption."
                    )
                )
            )

        else:

            items.append(
                BudgetItem(
                    category="miscellaneous",
                    amount=None,
                    status="unavailable",
                    basis=(
                        "No miscellaneous-cost "
                        "assumption is available."
                    )
                )
            )

        # -------------------------------------------------
        # Activities
        # -------------------------------------------------

        items.append(
            BudgetItem(
                category="activities",
                amount=None,
                status="unavailable",
                basis=(
                    "The current destination dataset "
                    "contains activities but does not "
                    "contain activity prices."
                )
            )
        )

        # -------------------------------------------------
        # Intercity transport
        # -------------------------------------------------

        items.append(
            BudgetItem(
                category="intercity_transport",
                amount=None,
                status="unavailable",
                basis=(
                    "The current system does not have "
                    "live or stored intercity transport prices."
                )
            )
        )

        # -------------------------------------------------
        # Calculate partial total
        # -------------------------------------------------

        known_amounts = [
            item.amount
            for item in items
            if item.amount is not None
        ]

        if known_amounts:

            total = sum(known_amounts)

            total_status = "partial_estimate"

            assumptions.append(
                "Total excludes unavailable costs "
                "such as activity and intercity transport."
            )

        else:

            total = None

            total_status = "unavailable"

        # -------------------------------------------------
        # Estimation assumptions
        # -------------------------------------------------

        assumptions.extend(
            [
                "Amounts are generic planning estimates.",
                "Amounts are not live destination prices.",
                (
                    "Actual costs may vary by destination, "
                    "season, availability, and traveler choices."
                )
            ]
        )

        # -------------------------------------------------
        # Return budget plan
        # -------------------------------------------------

        return BudgetPlan(
            destination=destination.name,
            duration_days=duration,
            budget_tier=budget_tier,
            items=items,
            total=total,
            total_status=total_status,
            assumptions=assumptions
        )
