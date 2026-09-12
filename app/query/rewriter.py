from langchain_ollama import ChatOllama


class QueryRewriter:

    def __init__(self, model_name: str):

        self.llm = ChatOllama(
            model=model_name,
            temperature=0
        )

    def rewrite(self, query_analysis):

        prompt = f"""
You are a travel search query rewriter.

Convert the following structured travel requirements
into a concise natural-language search query.

The query will be used to retrieve relevant travel
destinations from a knowledge base.

Travel requirements:
Intent: {query_analysis.intent}
Travel styles: {query_analysis.travel_styles}
Best for: {query_analysis.best_for}
Budget: {query_analysis.budget}
Duration: {query_analysis.duration_days} days
Location: {query_analysis.location}
Activities: {query_analysis.activities}
Avoid: {query_analysis.avoid}

Create only the search query.
Do not provide recommendations.
Do not explain anything.
"""

        response = self.llm.invoke(prompt)

        return response.content.strip()