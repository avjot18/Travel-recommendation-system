import re


class DestinationRanker:

    def _duration_matches(
        self,
        user_days,
        destination_duration
    ):

        if not user_days or not destination_duration:
            return False

        if isinstance(destination_duration, list):

            if len(destination_duration) >= 2:

                minimum = destination_duration[0]
                maximum = destination_duration[1]

                return minimum <= user_days <= maximum

            return False

        if isinstance(destination_duration, str):

            numbers = re.findall(
                r"\d+",
                destination_duration
            )

            if len(numbers) >= 2:

                minimum = int(numbers[0])
                maximum = int(numbers[1])

                return minimum <= user_days <= maximum

            if len(numbers) == 1:

                return int(numbers[0]) == user_days

        return False


    def _text_matches(
        self,
        user_values,
        destination_values
    ):

        if not user_values or not destination_values:
            return 0

        user_values = [
            value.lower()
            for value in user_values
        ]

        destination_values = [
            value.lower()
            for value in destination_values
        ]

        matches = 0

        for user_value in user_values:

            if user_value in destination_values:
                matches += 1

        return matches


    def rank(self, documents, query_analysis):

        ranked = []

        for document in documents:

            metadata = document.metadata

            score = 0


            # Travel style
            style_matches = self._text_matches(
                query_analysis.travel_styles,
                metadata.get("travel_styles", [])
            )

            score += style_matches * 2


            # Best for
            best_for_matches = self._text_matches(
                query_analysis.best_for,
                metadata.get("best_for", [])
            )

            score += best_for_matches * 3


            # Budget
            destination_budget = metadata.get(
                "budget_tier"
            )

            if (
                query_analysis.budget
                and destination_budget
            ):

                if (
                    query_analysis.budget.lower()
                    == destination_budget.lower()
                ):
                    score += 2
                else:
                    score -= 2


            # Duration
            if self._duration_matches(
                query_analysis.duration_days,
                metadata.get("ideal_duration_days")
            ):
                score += 2


            ranked.append(
                {
                    "document": document,
                    "score": score
                }
            )


        ranked.sort(
            key=lambda item: item["score"],
            reverse=True
        )

        return ranked