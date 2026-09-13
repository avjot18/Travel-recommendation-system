from langchain_ollama import ChatOllama

class AnswerGenerator:

    def __init__(self, model_name: str = None):
        pass

    def generate(
        self,
        query,
        query_analysis,
        recommendation_decision
    ):

        candidate = recommendation_decision.get("candidate")

        if not candidate:
            return (
                "I could not find a suitable destination "
                "from the available data."
            )

        document = candidate["document"]
        metadata = document.metadata
        fit = candidate["requirement_fit"]

        destination = metadata.get("destination")
        duration = metadata.get("ideal_duration_days")

        direct_matches = fit.get("direct_matches", [])
        semantic_matches = fit.get("semantic_matches", [])
        possible_matches = fit.get("possible_matches", [])
        unknowns = fit.get("unknowns", [])
        mismatches = fit.get("mismatches", [])

        why = []

        # Duration
        if "duration" in direct_matches and duration:
            if isinstance(duration, list) and len(duration) >= 2:
                why.append(
                    f"Your {query_analysis.duration_days}-day trip "
                    f"fits the listed ideal duration of "
                    f"{duration[0]}–{duration[1]} days."
                )
            else:
                why.append(
                    f"Your {query_analysis.duration_days}-day trip "
                    f"matches the listed ideal duration."
                )

        # Travelers
        for traveler in query_analysis.travelers:
            if traveler in direct_matches:
                why.append(
                    f"{destination} is explicitly listed as "
                    f"suitable for {traveler}."
                )

        # Semantic matches
        for match in semantic_matches:
            why.append(
                f"The available data shows a possible match "
                f"for {match}."
            )

        # Possible matches
        if "location" in possible_matches:
            why.append(
                "The destination is a possible match for "
                "your requested mountain setting."
            )

        # Fallback
        if not why:
            why.append(
                "It is the highest-ranked available candidate "
                "for your requirements."
            )

        limitations = []

        for unknown in unknowns:
            if unknown == "peaceful":
                limitations.append(
                    "The current data does not verify whether "
                    "the destination is peaceful."
                )

            elif unknown == "extreme cold avoidance":
                limitations.append(
                    "The current data does not verify whether "
                    "extreme cold can be avoided."
                )

            elif unknown == "budget":
                limitations.append(
                    "The current data does not verify whether "
                    "the destination fits your budget."
                )

            elif "suitability" in unknown:
                limitations.append(
                    f"The current data does not fully verify "
                    f"{unknown}."
                )

            else:
                limitations.append(
                    f"The current data does not verify {unknown}."
                )

        # Actual mismatches are different from unknowns.
        for mismatch in mismatches:
            limitations.append(
                f"The destination does not match your "
                f"{mismatch} requirement."
            )

        answer = f"Recommendation: {destination}\n\n"

        answer += "Why:\n"
        for reason in why:
            answer += f"- {reason}\n"

        if limitations:
            answer += "\nLimitations:\n"
            for limitation in limitations:
                answer += f"- {limitation}\n"

        return answer.strip()