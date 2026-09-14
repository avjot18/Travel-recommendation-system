import re


class DestinationRanker:

    # Hard requirements have a stronger influence
    HARD_WEIGHTS = {
        "duration": 25,
        "budget": 25,
    }

    # Soft preferences influence ranking but should not dominate
    SOFT_WEIGHTS = {
        "location": 20,
        "traveler": 10,
        "travel_style": 10,
        "interest": 5,
        "activity": 10,
        "season": 5,
        "pace": 5,
    }

    SEMANTIC_THRESHOLD = 0.45

    def __init__(self, embeddings):
        self.embeddings = embeddings

    # ---------------------------------------------------------
    # Utility
    # ---------------------------------------------------------

    def _normalize(self, value):
        return str(value).lower().strip()

    def _semantic_similarity(
        self,
        user_value,
        destination_values
    ):

        if not user_value or not destination_values:
            return 0.0

        user_embedding = self.embeddings.embed_query(
            user_value
        )

        destination_embeddings = (
            self.embeddings.embed_documents(
                destination_values
            )
        )

        user_norm = sum(
            value * value
            for value in user_embedding
        ) ** 0.5

        if user_norm == 0:
            return 0.0

        best_similarity = 0.0

        for destination_embedding in destination_embeddings:

            destination_norm = sum(
                value * value
                for value in destination_embedding
            ) ** 0.5

            if destination_norm == 0:
                continue

            dot_product = sum(
                a * b
                for a, b in zip(
                    user_embedding,
                    destination_embedding
                )
            )

            similarity = (
                dot_product
                / (user_norm * destination_norm)
            )

            best_similarity = max(
                best_similarity,
                similarity
            )

        return best_similarity

    def _match_type(
        self,
        user_value,
        destination_values
    ):

        if not user_value or not destination_values:
            return "unknown", 0.0

        normalized_user = self._normalize(
            user_value
        )

        normalized_destination = {
            self._normalize(value)
            for value in destination_values
            if value
        }

        # Exact match
        if normalized_user in normalized_destination:
            return "direct", 1.0

        # Semantic match
        similarity = self._semantic_similarity(
            normalized_user,
            list(normalized_destination)
        )

        if similarity >= self.SEMANTIC_THRESHOLD:
            return "semantic", similarity

        return "unknown", similarity

    # ---------------------------------------------------------
    # Duration
    # ---------------------------------------------------------

    def _duration_relation(
        self,
        user_days,
        destination_duration
    ):

        if (
            user_days is None
            or destination_duration is None
        ):
            return "unknown"

        if isinstance(
            destination_duration,
            list
        ):

            if len(destination_duration) >= 2:

                minimum = destination_duration[0]
                maximum = destination_duration[1]

                if minimum <= user_days <= maximum:
                    return "match"

                return "mismatch"

            if len(destination_duration) == 1:

                if destination_duration[0] == user_days:
                    return "match"

                return "mismatch"

        if isinstance(
            destination_duration,
            str
        ):

            numbers = re.findall(
                r"\d+",
                destination_duration
            )

            if len(numbers) >= 2:

                minimum = int(numbers[0])
                maximum = int(numbers[1])

                if minimum <= user_days <= maximum:
                    return "match"

                return "mismatch"

            if len(numbers) == 1:

                if int(numbers[0]) == user_days:
                    return "match"

                return "mismatch"

        return "unknown"

    # ---------------------------------------------------------
    # Location
    # ---------------------------------------------------------

    def _location_relation(
        self,
        requested_location,
        metadata
    ):

        if not requested_location:
            return "unknown"

        requested_location = self._normalize(
            requested_location
        )

        destination = self._normalize(
            metadata.get("destination", "")
        )

        state = self._normalize(
            metadata.get("state", "")
        )

        region = self._normalize(
            metadata.get("region", "")
        )

        # Exact location match
        if requested_location in {
            destination,
            state,
            region
        }:
            return "match"

        # Dataset currently does not contain
        # a dedicated geographic-type field.
        #
        # Therefore mountain/beach/desert style
        # geographic requests are treated cautiously.

        if requested_location in {
            "mountain",
            "mountains",
            "hill",
            "hills"
        }:

            mountain_states = {
                "himachal pradesh",
                "uttarakhand",
                "ladakh",
                "jammu and kashmir",
                "sikkim",
                "arunachal pradesh"
            }

            if state in mountain_states:
                return "possible"

        return "mismatch"

    # ---------------------------------------------------------
    # Budget
    # ---------------------------------------------------------

    def _budget_relation(
        self,
        user_budget,
        destination_budget
    ):

        if not user_budget:
            return "unknown"

        if not destination_budget:
            return "unknown"

        user_budget = self._normalize(
            user_budget
        )

        destination_budget = self._normalize(
            destination_budget
        )

        if user_budget == destination_budget:
            return "match"

        return "mismatch"

    # ---------------------------------------------------------
    # Generic matching
    # ---------------------------------------------------------

    def _evaluate_values(
        self,
        user_values,
        destination_values,
        weight,
        label,
        score,
        direct_matches,
        semantic_matches,
        unknowns
    ):

        for user_value in user_values:

            match_type, similarity = (
                self._match_type(
                    user_value,
                    destination_values
                )
            )

            if match_type == "direct":

                score += weight

                direct_matches.append(
                    user_value
                )

            elif match_type == "semantic":

                score += weight * 0.6

                semantic_matches.append(
                    f"{user_value} {label}"
                )

            else:

                unknowns.append(
                    f"{user_value} {label}"
                )

        return score

    # ---------------------------------------------------------
    # Main ranking
    # ---------------------------------------------------------

    def rank(
        self,
        documents,
        travel_profile
    ):

        ranked = []

        for document in documents:

            metadata = document.metadata

            score = 0

            direct_matches = []
            semantic_matches = []
            possible_matches = []
            unknowns = []
            mismatches = []

            # =================================================
            # LOCATION
            # =================================================

            location = self._location_relation(
                travel_profile.location,
                metadata
            )

            if location == "match":

                score += self.SOFT_WEIGHTS[
                    "location"
                ]

                direct_matches.append(
                    "location"
                )

            elif location == "possible":

                score += (
                    self.SOFT_WEIGHTS["location"]
                    * 0.75
                )

                possible_matches.append(
                    "location"
                )

            elif location == "mismatch":

                mismatches.append(
                    "location"
                )

            else:

                unknowns.append(
                    "location"
                )

            # =================================================
            # DURATION
            # =================================================

            duration = self._duration_relation(
                travel_profile.duration_days,
                metadata.get(
                    "ideal_duration_days"
                )
            )

            if duration == "match":

                score += self.HARD_WEIGHTS[
                    "duration"
                ]

                direct_matches.append(
                    "duration"
                )

            elif duration == "mismatch":

                score -= self.HARD_WEIGHTS[
                    "duration"
                ]

                mismatches.append(
                    "duration"
                )

            else:

                unknowns.append(
                    "duration"
                )

            # =================================================
            # BUDGET
            # =================================================

            budget = self._budget_relation(
                travel_profile.budget_range,
                metadata.get("budget_tier")
            )

            if budget == "match":

                score += self.HARD_WEIGHTS[
                    "budget"
                ]

                direct_matches.append(
                    "budget"
                )

            elif budget == "mismatch":

                score -= self.HARD_WEIGHTS[
                    "budget"
                ]

                mismatches.append(
                    "budget"
                )

            elif (
                travel_profile.budget_range
                and not metadata.get("budget_tier")
            ):

                unknowns.append(
                    "budget"
                )

            # =================================================
            # TRAVELERS
            # =================================================

            score = self._evaluate_values(
                travel_profile.travelers,
                metadata.get("best_for", []),
                self.SOFT_WEIGHTS["traveler"],
                "suitability",
                score,
                direct_matches,
                semantic_matches,
                unknowns
            )

            # =================================================
            # TRAVEL STYLES
            # =================================================

            score = self._evaluate_values(
                travel_profile.travel_styles,
                metadata.get("travel_styles", []),
                self.SOFT_WEIGHTS["travel_style"],
                "travel style",
                score,
                direct_matches,
                semantic_matches,
                unknowns
            )

            # =================================================
            # INTERESTS
            # =================================================

            destination_interests = (
                metadata.get("best_for", [])
                + metadata.get("activities", [])
            )

            score = self._evaluate_values(
                travel_profile.interests,
                destination_interests,
                self.SOFT_WEIGHTS["interest"],
                "interest",
                score,
                direct_matches,
                semantic_matches,
                unknowns
            )

            # =================================================
            # ACTIVITIES
            # =================================================

            score = self._evaluate_values(
                travel_profile.activities,
                metadata.get("activities", []),
                self.SOFT_WEIGHTS["activity"],
                "activity",
                score,
                direct_matches,
                semantic_matches,
                unknowns
            )

            # =================================================
            # SEASON
            # =================================================

            if travel_profile.season:

                # Current dataset has best_months,
                # but no normalized season field.

                best_months = metadata.get(
                    "best_months"
                )

                if best_months:

                    match_type, similarity = (
                        self._match_type(
                            travel_profile.season,
                            best_months
                        )
                    )

                    if match_type == "direct":

                        score += self.SOFT_WEIGHTS[
                            "season"
                        ]

                        direct_matches.append(
                            "season"
                        )

                    elif match_type == "semantic":

                        score += (
                            self.SOFT_WEIGHTS["season"]
                            * 0.6
                        )

                        semantic_matches.append(
                            "season compatibility"
                        )

                    else:

                        unknowns.append(
                            "season compatibility"
                        )

                else:

                    unknowns.append(
                        "season compatibility"
                    )

            # =================================================
            # PACE
            # =================================================

            if travel_profile.pace:

                # Pace is not currently represented
                # in the dataset.

                unknowns.append(
                    "pace compatibility"
                )

            # =================================================
            # AVOIDANCES
            # =================================================

            for avoid in travel_profile.avoids:

                if avoid == "extreme_cold":

                    unknowns.append(
                        "extreme cold avoidance"
                    )

                elif avoid == "crowds":

                    unknowns.append(
                        "crowd avoidance"
                    )

                elif avoid == "hectic":

                    unknowns.append(
                        "hectic itinerary avoidance"
                    )

                else:

                    unknowns.append(
                        f"{avoid} avoidance"
                    )

            # =================================================
            # RESULT
            # =================================================

            ranked.append({
                "document": document,
                "score": round(score, 2),
                "explanation": {
                    "direct_matches": direct_matches,
                    "semantic_matches": semantic_matches,
                    "possible_matches": possible_matches,
                    "unknowns": unknowns,
                    "mismatches": mismatches
                }
            })

        ranked.sort(
            key=lambda item: item["score"],
            reverse=True
        )

        return ranked