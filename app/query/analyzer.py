from langchain_ollama import ChatOllama
from pydantic import BaseModel


class QueryAnalysis(BaseModel):
    intent: str
    travel_styles: list[str]
    best_for: list[str]
    budget: str | None
    duration_days: int | None
    location: str | None
    activities: list[str]
    avoid: list[str]


class QueryAnalyzer:

    def __init__(self, model_name: str):

        self.llm = ChatOllama(
            model=model_name,
            temperature=0
        )

        self.structured_llm = self.llm.with_structured_output(
            QueryAnalysis
        )

    def analyze(self, query: str):

        prompt = f"""
You are a travel query analyzer.

Analyze the user's travel request and extract:
- intent
- travel styles
- suitable traveler types
- budget
- duration in days
- location preference
- activities
- things to avoid

If a value is not mentioned, use null for single-value fields
and an empty list for list fields.

User query:
{query}
"""

        response = self.structured_llm.invoke(prompt)

        return response