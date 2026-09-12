from langchain_ollama import ChatOllama


class AnswerGenerator:

    def __init__(self, model_name: str):

        self.llm = ChatOllama(
            model=model_name,
            temperature=0
        )

    def generate(
        self,
        query: str,
        query_analysis,
        ranked_destinations
    ):

        candidates = []

        for item in ranked_destinations:

            document = item["document"]
            score = item["score"]

            candidates.append(
                f"""
Destination: {document.metadata.get("destination")}
State: {document.metadata.get("state")}
Score: {score}

Information:
{document.page_content}
""".strip()
            )

        context = "\n\n---\n\n".join(candidates)

        prompt = f"""
You are a helpful India travel recommendation assistant.

Answer the user's travel request using ONLY the candidate
destinations provided below.

Do not invent facts that are not present in the candidates.

User request:
{query}

User requirements:
Intent: {query_analysis.intent}
Travel styles: {query_analysis.travel_styles}
Best for: {query_analysis.best_for}
Budget: {query_analysis.budget}
Duration: {query_analysis.duration_days} days
Location: {query_analysis.location}
Activities: {query_analysis.activities}
Avoid: {query_analysis.avoid}

Candidate destinations:
{context}

Instructions:

1. Recommend the best destination(s) from the candidates.
2. Explain briefly why they fit the user's requirements.
3. Mention important trade-offs when relevant.
4. Do not claim that something is suitable if the provided
   information does not support it.
5. Do not invent prices, weather, opening hours, travel times,
   ratings, or other facts.
6. If the candidates are not a strong match, say so honestly.
7. Keep the answer concise and useful.

Answer the user directly.
"""

        response = self.llm.invoke(prompt)

        return response.content.strip()