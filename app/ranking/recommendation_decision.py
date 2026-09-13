class RecommendationDecision:

    def decide(self, evaluated_destinations):

        if not evaluated_destinations:
            return {
                "status": "no_candidate",
                "candidate": None,
                "alternatives": []
            }

        # Ignore candidates that have explicit mismatches
        viable_candidates = [
            item
            for item in evaluated_destinations
            if item["requirement_fit"]["status"] != "poor_fit"
        ]

        if not viable_candidates:
            return {
                "status": "no_good_match",
                "candidate": None,
                "alternatives": []
            }

        # The ranker has already sorted candidates by score.
        # Therefore the first viable candidate is our winner.
        candidate = viable_candidates[0]

        alternatives = viable_candidates[1:3]

        return {
            "status": candidate["requirement_fit"]["status"],
            "candidate": candidate,
            "alternatives": alternatives
        }