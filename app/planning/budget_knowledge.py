
class BudgetKnowledge:

    """
    Generic travel-cost assumptions.

    These values are planning assumptions only.
    They are NOT live destination prices.
    """

    BUDGET_ASSUMPTIONS = {

        "low": {
            "accommodation_per_day": 1000,
            "food_per_day": 500,
            "local_transport_per_day": 300,
            "miscellaneous_per_day": 200,
        },

        "mid-range": {
            "accommodation_per_day": 2500,
            "food_per_day": 1000,
            "local_transport_per_day": 600,
            "miscellaneous_per_day": 400,
        },

        "luxury": {
            "accommodation_per_day": 6000,
            "food_per_day": 2500,
            "local_transport_per_day": 1200,
            "miscellaneous_per_day": 800,
        },
    }

    @classmethod
    def get_assumptions(
        cls,
        budget_tier: str | None
    ) -> dict:

        if not budget_tier:
            return {}

        normalized_tier = (
            budget_tier
            .strip()
            .lower()
        )

        return cls.BUDGET_ASSUMPTIONS.get(
            normalized_tier,
            {}
        )

