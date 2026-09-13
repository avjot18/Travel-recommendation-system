from langchain_ollama import ChatOllama
from pydantic import BaseModel


class ClaimEvaluation(BaseModel):
    claim: str
    classification: str
    explanation: str


class GroundednessResult(BaseModel):
    grounded: bool
    claims: list[ClaimEvaluation]
    explanation: str


class GroundednessChecker:

    def __init__(self, model_name: str, claim_checker):

        self.llm = ChatOllama(
            model=model_name,
            temperature=0
        )

        self.structured_llm = (
            self.llm.with_structured_output(
                GroundednessResult
            )
        )

        self.claim_checker = claim_checker

    def check(
        self,
        answer,
        documents,
        requirement_fit
    ):

        # ------------------------------------------
        # 1. Detect potentially risky claims
        # ------------------------------------------

        risky_claims = (
            self.claim_checker.find_risky_claims(
                answer
            )
        )

        print("\nRISKY CLAIMS:")
        print("------------------------")

        for claim in risky_claims:

            print(
                f"{claim['category']}: "
                f"{claim['claim']}"
            )

        # ------------------------------------------
        # 2. Build requirement-fit context
        # ------------------------------------------

        fit_context = f"""
Direct matches:
{requirement_fit.get("direct_matches", [])}

Semantic matches:
{requirement_fit.get("semantic_matches", [])}

Possible matches:
{requirement_fit.get("possible_matches", [])}

Unknown requirements:
{requirement_fit.get("unknowns", [])}

Mismatches:
{requirement_fit.get("mismatches", [])}
""".strip()

        # ------------------------------------------
        # 3. Build evidence context
        # ------------------------------------------

        evidence = []

        for document in documents:

            evidence.append(
                f"""
Destination:
{document.metadata.get("destination")}

State:
{document.metadata.get("state")}

Information:
{document.page_content}
""".strip()
            )

        context = "\n\n---\n\n".join(
            evidence
        )

        # ------------------------------------------
        # 4. Groundedness evaluation prompt
        # ------------------------------------------

        prompt = f"""
You are a strict factual-grounding evaluator
for an India travel recommendation system.

Your job is to check whether factual claims in the
assistant answer are supported by the provided evidence.

IMPORTANT:

Do NOT judge whether the recommendation itself is good.

Only judge whether the claims made in the answer are
supported by the evidence.

Classify every meaningful claim as exactly one of:

SUPPORTED
    The evidence explicitly supports the claim.

REASONABLE_INFERENCE
    The claim is a cautious recommendation inference
    derived from the evidence.

UNSUPPORTED
    The answer presents a factual claim that cannot
    be established from the evidence.

UNKNOWN_STATEMENT
    The answer explicitly says that something could
    not be verified or is unknown.


IMPORTANT RULES:

1. Extract meaningful factual claims from the answer.

2. Check every claim against the provided evidence.

3. Do not use outside travel knowledge.

4. Claims about weather, climate, temperature,
   prices, affordability, safety, travel time,
   hotels, restaurants, or opening hours require
   explicit evidence.

5. If the evidence does not mention something,
   a factual statement about it is UNSUPPORTED.

6. A cautious recommendation inference can be
   REASONABLE_INFERENCE.

7. An UNKNOWN_STATEMENT is acceptable.

8. Do not treat a recommendation inference as an
   explicit factual match.

9. The final grounded value must be FALSE if there
   is any meaningful UNSUPPORTED claim.

10. SUPPORTED and REASONABLE_INFERENCE claims are
    acceptable.

11. UNKNOWN_STATEMENT claims are acceptable.


========================================
REQUIREMENT FIT — AUTHORITATIVE
========================================

The following requirement evaluation was produced
by the application's requirement-fit evaluator.

Treat it as authoritative.

{fit_context}


IMPORTANT REQUIREMENT-FIT RULES:

12. If a requirement appears under UNKNOWN,
    the assistant must NOT present that requirement
    as a verified fact.

13. If a requirement appears under MISMATCH,
    the assistant must NOT claim that the destination
    satisfies that requirement.

14. Do not reinterpret UNKNOWN as MATCH.

15. Do not reinterpret MISMATCH as MATCH.

16. An UNKNOWN requirement is not evidence that the
    requirement is satisfied.

17. An UNKNOWN requirement is also NOT evidence that
    the requirement is violated.

18. Therefore, UNKNOWN should be described as
    "unverified", "not established", or
    "not available in the current data".


========================================
EXAMPLES
========================================

Requirement fit:

Unknown:
["peaceful"]

Assistant claim:
"Manali is peaceful."

Classification:
UNSUPPORTED


Assistant statement:
"The available data does not verify whether Manali
meets the peaceful requirement."

Classification:
UNKNOWN_STATEMENT


Requirement fit:

Unknown:
["extreme cold avoidance"]

Assistant claim:
"Manali avoids extreme cold."

Classification:
UNSUPPORTED


Assistant statement:
"The available data does not verify whether Manali
avoids extreme cold."

Classification:
UNKNOWN_STATEMENT


Requirement fit:

Mismatch:
["budget"]

Assistant claim:
"Manali is suitable for a low-budget trip."

Classification:
UNSUPPORTED


========================================
RISKY CLAIMS DETECTED
========================================

{risky_claims}


========================================
EVIDENCE
========================================

{context}


========================================
ASSISTANT ANSWER
========================================

{answer}


========================================
FINAL INSTRUCTION
========================================

Evaluate the answer claim-by-claim.

Be conservative.

If the evidence does not explicitly support
a factual claim, classify it as UNSUPPORTED.

Return a structured evaluation.
"""

        # ------------------------------------------
        # 5. Ask the LLM judge
        # ------------------------------------------

        result = self.structured_llm.invoke(
            prompt
        )

        return result