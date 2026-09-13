import re


class DestinationRanker:

    HARD_WEIGHTS = {
        "location": 30,
        "duration": 25,
        "budget": 25
    }

    SOFT_WEIGHTS = {
        "traveler": 10,
        "preference": 10,
        "activity": 10
    }

    SEMANTIC_THRESHOLD = 0.45

    def __init__(self, embeddings):
        self.embeddings = embeddings

    # --------------------------------------------------
    # BASIC HELPERS
    # --------------------------------------------------

    def _normalize(self, value):
        return str(value).lower().strip()

    # --------------------------------------------------
    # SEMANTIC MATCHING
    # --------------------------------------------------

    def _semantic_similarity(self, user_value, destination_values):

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

        # We know something about the field,
        # but it isn't strong enough to call a match.
        return "unknown", similarity

    # --------------------------------------------------
    # DURATION
    # --------------------------------------------------

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

        if isinstance(destination_duration, list):

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

        if isinstance(destination_duration, str):

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

    # --------------------------------------------------
    # LOCATION
    # --------------------------------------------------

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

        # Direct location match
        if requested_location in {
            destination,
            state,
            region
        }:
            return "match"

        # Heuristic geographic relationship
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

    # --------------------------------------------------
    # MAIN RANKING
    # --------------------------------------------------

    def rank(
        self,
        documents,
        query_analysis
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

            # ==========================================
            # LOCATION
            # ==========================================

            location = self._location_relation(
                query_analysis.location,
                metadata
            )

            if location == "match":

                score += self.HARD_WEIGHTS["location"]

                direct_matches.append(
                    "location"
                )

            elif location == "possible":

                score += 15

                possible_matches.append(
                    "location"
                )

            elif location == "mismatch":

                score -= self.HARD_WEIGHTS["location"]

                mismatches.append(
                    "location"
                )

            else:

                unknowns.append(
                    "location"
                )

            # ==========================================
            # DURATION
            # ==========================================

            duration = self._duration_relation(
                query_analysis.duration_days,
                metadata.get("ideal_duration_days")
            )

            if duration == "match":

                score += self.HARD_WEIGHTS["duration"]

                direct_matches.append(
                    "duration"
                )

            elif duration == "mismatch":

                score -= self.HARD_WEIGHTS["duration"]

                mismatches.append(
                    "duration"
                )

            else:

                unknowns.append(
                    "duration"
                )

            # ==========================================
            # BUDGET
            # ==========================================

            user_budget = query_analysis.budget

            destination_budget = metadata.get(
                "budget_tier"
            )

            if user_budget:

                if destination_budget:

                    if (
                        self._normalize(user_budget)
                        ==
                        self._normalize(
                            destination_budget
                        )
                    ):

                        score += self.HARD_WEIGHTS[
                            "budget"
                        ]

                        direct_matches.append(
                            "budget"
                        )

                    else:

                        score -= self.HARD_WEIGHTS[
                            "budget"
                        ]

                        mismatches.append(
                            "budget"
                        )

                else:

                    unknowns.append(
                        "budget"
                    )

            # ==========================================
            # TRAVELER TYPE
            # ==========================================

            traveler_values = metadata.get(
                "best_for",
                []
            )

            for traveler in query_analysis.travelers:

                match_type, similarity = (
                    self._match_type(
                        traveler,
                        traveler_values
                    )
                )

                print(
                    f"[SEMANTIC] "
                    f"{traveler} -> "
                    f"{traveler_values} = "
                    f"{similarity:.3f}"
                )

                if match_type == "direct":

                    score += self.SOFT_WEIGHTS[
                        "traveler"
                    ]

                    direct_matches.append(
                        traveler
                    )

                elif match_type == "semantic":

                    score += (
                        self.SOFT_WEIGHTS[
                            "traveler"
                        ] * 0.6
                    )

                    semantic_matches.append(
                        f"{traveler} suitability"
                    )

                else:

                    unknowns.append(
                        f"{traveler} suitability"
                    )

            # ==========================================
            # PREFERENCES
            # ==========================================

            preference_values = metadata.get(
                "travel_styles",
                []
            )

            for preference in query_analysis.preferences:

                match_type, similarity = (
                    self._match_type(
                        preference,
                        preference_values
                    )
                )

                print(
                    f"[SEMANTIC] "
                    f"{preference} -> "
                    f"{preference_values} = "
                    f"{similarity:.3f}"
                )

                if match_type == "direct":

                    score += self.SOFT_WEIGHTS[
                        "preference"
                    ]

                    direct_matches.append(
                        preference
                    )

                elif match_type == "semantic":

                    score += (
                        self.SOFT_WEIGHTS[
                            "preference"
                        ] * 0.6
                    )

                    semantic_matches.append(
                        f"{preference} preference"
                    )

                else:

                    unknowns.append(
                        preference
                    )

            # ==========================================
            # ACTIVITIES
            # ==========================================

            activity_values = metadata.get(
                "activities",
                []
            )

            for activity in query_analysis.activities:

                match_type, similarity = (
                    self._match_type(
                        activity,
                        activity_values
                    )
                )

                print(
                    f"[SEMANTIC] "
                    f"{activity} -> "
                    f"{activity_values} = "
                    f"{similarity:.3f}"
                )

                if match_type == "direct":

                    score += self.SOFT_WEIGHTS[
                        "activity"
                    ]

                    direct_matches.append(
                        activity
                    )

                elif match_type == "semantic":

                    score += (
                        self.SOFT_WEIGHTS[
                            "activity"
                        ] * 0.6
                    )

                    semantic_matches.append(
                        f"{activity} activity"
                    )

                else:

                    unknowns.append(
                        f"{activity} activity"
                    )

            # ==========================================
            # NEGATIVE CONSTRAINTS
            # ==========================================

            for constraint in query_analysis.constraints:

                if constraint == "avoid_extreme_cold":

                    unknowns.append(
                        "extreme cold avoidance"
                    )

            # ==========================================
            # STORE RESULT
            # ==========================================

            ranked.append({

                "document": document,

                "score": round(
                    score,
                    2
                ),

                "explanation": {

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

        # Highest score first
        ranked.sort(
            key=lambda item: item["score"],
            reverse=True
        )

        return ranked