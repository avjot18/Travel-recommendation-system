import re


class ClaimChecker:

    UNSUPPORTED_FACT_PATTERNS = {

        "climate": [
            r"\bmild climate\b",
            r"\bpleasant climate\b",
            r"\bextreme cold\b",
            r"\bavoids? extreme cold\b",
            r"\bnot very cold\b",
            r"\bwarm\b",
            r"\bcold\b",
            r"\bhot\b",
            r"\btemperature\b",
            r"\bweather\b",
        ],

        "affordability": [
            r"\bcheap\b",
            r"\baffordable\b",
            r"\bbudget[- ]friendly\b",
            r"\blow[- ]budget\b",
            r"\binexpensive\b",
            r"\bcosts?\b",
            r"\bprice\b",
            r"\bprices\b",
        ],

        "safety": [
            r"\bsafe\b",
            r"\bsafest\b",
            r"\bdangerous\b",
            r"\bsafety\b",
        ],

        "travel_time": [
            r"\b\d+\s*(?:hour|hours|hr|hrs)\b",
            r"\b\d+\s*(?:km|kilometers|kilometres)\b",
            r"\btakes?\s+\w+\s+to\s+reach\b",
        ],
    }

    def find_risky_claims(self, answer):

        risky_claims = []

        sentences = re.split(
            r"(?<=[.!?])\s+",
            answer.strip()
        )

        for sentence in sentences:

            sentence_lower = sentence.lower()

            for category, patterns in (
                self.UNSUPPORTED_FACT_PATTERNS.items()
            ):

                for pattern in patterns:

                    if re.search(
                        pattern,
                        sentence_lower
                    ):

                        risky_claims.append({
                            "claim": sentence.strip(),
                            "category": category
                        })

                        break

        return risky_claims