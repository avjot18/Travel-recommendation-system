class QueryRewriter:

    def rewrite(self, query_analysis):

        parts = []

        # Location
        if query_analysis.location:
            parts.append(query_analysis.location)

        # Duration
        if query_analysis.duration_days:
            parts.append(
                f"{query_analysis.duration_days} day trip"
            )

        # Budget
        if query_analysis.budget:
            parts.append(
                f"{query_analysis.budget} budget"
            )

        # Travelers
        if query_analysis.travelers:
            parts.extend(
                query_analysis.travelers
            )

        # Preferences
        if query_analysis.preferences:
            parts.extend(
                query_analysis.preferences
            )

        # Activities
        if query_analysis.activities:
            parts.extend(
                query_analysis.activities
            )

        # Constraints
        if query_analysis.constraints:
            parts.extend(
                query_analysis.constraints
            )

        return " ".join(parts)