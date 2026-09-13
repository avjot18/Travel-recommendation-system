class RequirementFitEvaluator:

    def evaluate(self, ranked_destinations):

        evaluated = []

        for item in ranked_destinations:

            explanation = item["explanation"]

            direct_matches = explanation.get(
                "direct_matches",
                []
            )

            semantic_matches = explanation.get(
                "semantic_matches",
                []
            )

            possible_matches = explanation.get(
                "possible_matches",
                []
            )

            unknowns = explanation.get(
                "unknowns",
                []
            )

            mismatches = explanation.get(
                "mismatches",
                []
            )

            # ------------------------------------------
            # Count evidence
            # ------------------------------------------

            strong_evidence = (
                len(direct_matches)
                + len(semantic_matches)
            )

            weak_evidence = len(
                possible_matches
            )

            uncertainty = len(
                unknowns
            )

            mismatch_count = len(
                mismatches
            )

            # ------------------------------------------
            # Determine fit status
            # ------------------------------------------

            if mismatch_count > 0:

                fit_status = "poor_fit"

            elif uncertainty > 0:

                fit_status = "partial_fit"

            elif weak_evidence > 0:

                fit_status = "partial_fit"

            else:

                fit_status = "strong_fit"

            # ------------------------------------------
            # Calculate confidence
            # ------------------------------------------

            total_requirements = (
                strong_evidence
                + weak_evidence
                + uncertainty
                + mismatch_count
            )

            if total_requirements == 0:

                confidence = 0.0

            else:

                confidence = (
                    strong_evidence
                    + (weak_evidence * 0.5)
                ) / total_requirements

            evaluated.append({

                **item,

                "requirement_fit": {

                    "status": fit_status,

                    "confidence": round(
                        confidence,
                        2
                    ),

                    "direct_matches":
                        direct_matches,

                    "semantic_matches":
                        semantic_matches,

                    "possible_matches":
                        possible_matches,

                    "unknowns":
                        unknowns,

                    "mismatches":
                        mismatches
                }
            })

        return evaluated