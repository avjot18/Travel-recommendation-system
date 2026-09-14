
import json

from app.planning.budget_knowledge import (
    BudgetKnowledge
)

from app.destination.builder import (
    DestinationProfileBuilder
)

from app.planning.budget_estimator import (
    BudgetEstimator
)

from app.planning.budget_knowledge import BudgetKnowledge
from app.query.analyzer import (
    QueryAnalyzer
)


DATA_PATH = (
    "data/"
    "india_travel_knowledge_base_v2_fully_populated.json"
)


def main():

    # -------------------------------------------------
    # Load dataset
    # -------------------------------------------------

    with open(
        DATA_PATH,
        "r",
        encoding="utf-8"
    ) as file:

        data = json.load(file)

    # -------------------------------------------------
    # Build destination
    # -------------------------------------------------

    builder = (
        DestinationProfileBuilder()
    )

    manali_data = next(
        destination
        for destination
        in data["destinations"]
        if destination["name"]
        == "Manali"
    )

    destination = (
        builder.build_destination(
            manali_data
        )
    )

    # -------------------------------------------------
    # Analyze query
    # -------------------------------------------------

    query = (
        "I have 4 days and want a "
        "peaceful mountain trip with "
        "my girlfriend. My budget is low."
    )

    analyzer = QueryAnalyzer()

    travel_profile = (
        analyzer.analyze(query)
    )

    print("DEBUG budget_range:", travel_profile.budget_range)

    print(
    "DEBUG assumptions:",
    BudgetKnowledge.get_assumptions(
        travel_profile.budget_range
    )
)

    # -------------------------------------------------
    # Estimate budget
    # -------------------------------------------------

    estimator = BudgetEstimator()

    budget = estimator.estimate(
        travel_profile,
        destination
    )

    # -------------------------------------------------
    # Display
    # -------------------------------------------------

    print("\nBUDGET PLAN")
    print("===========")

    print(
        "Destination:",
        budget.destination
    )

    print(
        "Duration:",
        budget.duration_days,
        "days"
    )

    for item in budget.items:

        print(
            f"\n{item.category}"
        )

        print(
            "Amount:",
            item.amount
        )

        print(
            "Status:",
            item.status
        )

        print(
            "Basis:",
            item.basis
        )

    print(
        "\nTotal:",
        budget.total
    )

    print(
        "Total status:",
        budget.total_status
    )


if __name__ == "__main__":
    main()

