from langchain_ollama import ChatOllama
from pydantic import BaseModel


class GroundednessResult(BaseModel):
    grounded: bool
    explanation: str


class GroundednessChecker:

    def __init__(self, model_name: str):

        self.llm = ChatOllama(
            model=model_name,
            temperature=0
        )

        self.structured_llm = self.llm.with_structured_output(
            GroundednessResult
        )

    def check(
        self,
        answer: str,
        documents
    ):

        evidence = []

        for document in documents:

            evidence.append(
                f"""
Destination: {document.metadata.get("destination")}
State: {document.metadata.get("state")}

Information:
{document.page_content}
""".strip()
            )

        context = "\n\n---\n\n".join(evidence)

        prompt = f"""
You are a strict factual grounding evaluator.

Your job is to determine whether the answer is supported
by the provided travel knowledge base.

IMPORTANT:

- Only information explicitly supported by the evidence
  should be considered grounded.
- Do not assume facts that are merely plausible.
- Do not use outside knowledge.
- If the answer contains unsupported claims, mark it
  as not grounded.

Evidence:
{context}

Answer:
{answer}

Determine whether the answer is fully grounded in the evidence.
"""

        result = self.structured_llm.invoke(prompt)

        return result