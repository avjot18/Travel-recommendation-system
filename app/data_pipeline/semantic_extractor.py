import json
from dataclasses import dataclass

from langchain_ollama import ChatOllama
from pydantic import BaseModel, Field

from app.data_pipeline.normalizer import NormalizedBlock


# ============================================================
# OUTPUT MODELS
# ============================================================

class SemanticActivity(BaseModel):
    name: str
    description: str | None = None


class SemanticAttraction(BaseModel):
    name: str
    description: str | None = None


class SemanticFood(BaseModel):
    name: str
    description: str | None = None


class SemanticExtraction(BaseModel):
    traveler_types: list[str] = Field(
        default_factory=list
    )

    pace: list[str] = Field(
        default_factory=list
    )

    crowd_level: str | None = None

    activities: list[SemanticActivity] = Field(
        default_factory=list
    )

    attractions: list[SemanticAttraction] = Field(
        default_factory=list
    )

    food_highlights: list[SemanticFood] = Field(
        default_factory=list
    )


@dataclass
class SemanticExtractionResult:
    extraction: SemanticExtraction
    source_blocks: list[NormalizedBlock]


# ============================================================
# SEMANTIC EXTRACTOR
# ============================================================

class SemanticExtractor:

    MAX_BLOCKS = 8
    MAX_CHARS = 6000

    def __init__(
        self,
        model_name: str = "qwen3:1.7b",
    ):
        self.llm = ChatOllama(
            model=model_name,
            temperature=0,
        )

    # ========================================================
    # PUBLIC API
    # ========================================================

    def extract(
        self,
        blocks: list[NormalizedBlock],
    ) -> SemanticExtractionResult:

        narrative_blocks = self._select_narrative_blocks(
            blocks
        )

        if not narrative_blocks:
            return SemanticExtractionResult(
                extraction=SemanticExtraction(),
                source_blocks=[],
            )

        source_text = self._build_source_text(
            narrative_blocks
        )

        prompt = self._build_prompt(
            source_text
        )

        response = self.llm.invoke(
            prompt
        )

        extraction = self._parse_response(
            response
        )

        return SemanticExtractionResult(
            extraction=extraction,
            source_blocks=narrative_blocks,
        )

    # ========================================================
    # SELECT RELEVANT BLOCKS
    # ========================================================

    def _select_narrative_blocks(
        self,
        blocks: list[NormalizedBlock],
    ) -> list[NormalizedBlock]:

        candidates = []

        for block in blocks:

            if block.block_type != "paragraph":
                continue

            text = self._clean_text(
                block.content
            )

            if not text:
                continue

            if len(text) < 80:
                continue

            if self._looks_like_article_title(
                text
            ):
                continue

            candidates.append(
                block
            )

        # Prefer longer narrative blocks because
        # they contain more factual context.
        candidates.sort(
            key=lambda block: len(
                self._clean_text(
                    block.content
                )
            ),
            reverse=True,
        )

        selected = []
        current_chars = 0

        for block in candidates:

            text = self._clean_text(
                block.content
            )

            if len(selected) >= self.MAX_BLOCKS:
                break

            if (
                current_chars + len(text)
                > self.MAX_CHARS
            ):
                continue

            selected.append(
                block
            )

            current_chars += len(text)

        return selected

    # ========================================================
    # SOURCE TEXT
    # ========================================================

    def _build_source_text(
        self,
        blocks: list[NormalizedBlock],
    ) -> str:

        parts = []

        for index, block in enumerate(
            blocks,
            start=1,
        ):

            text = self._clean_text(
                block.content
            )

            parts.append(
                f"[SOURCE BLOCK {index}]\n"
                f"{text}"
            )

        return "\n\n".join(
            parts
        )

    # ========================================================
    # PROMPT
    # ========================================================

    def _build_prompt(
        self,
        source_text: str,
    ) -> str:

        return f"""
You are an information extraction system.

Extract ONLY facts explicitly stated in the source.

SOURCE:
--------------------
{source_text}
--------------------

RULES:

1. Use ONLY the supplied source.

2. Do NOT use outside knowledge.

3. Do NOT infer traveler types.

4. Do NOT infer pace.

5. Do NOT infer crowd level.

6. Do NOT infer best seasons.

7. Extract an activity only if it is explicitly mentioned.

8. Extract an attraction only if it is explicitly mentioned.

9. Extract food only if it is explicitly mentioned.

10. Do not invent descriptions.

11. If a name is explicitly mentioned but no useful
    description is provided, use null.

12. Do not duplicate the same item.

13. Keep names concise.

14. Return ONLY valid JSON.

JSON FORMAT:

{{
    "traveler_types": [],
    "pace": [],
    "crowd_level": null,
    "activities": [
        {{
            "name": "",
            "description": null
        }}
    ],
    "attractions": [
        {{
            "name": "",
            "description": null
        }}
    ],
    "food_highlights": [
        {{
            "name": "",
            "description": null
        }}
    ]
}}
"""

    # ========================================================
    # RESPONSE PARSING
    # ========================================================

    def _parse_response(
        self,
        response,
    ) -> SemanticExtraction:

        content = response.content

        if not isinstance(
            content,
            str,
        ):
            content = str(
                content
            )

        content = content.strip()

        content = self._remove_code_fences(
            content
        )

        try:
            data = json.loads(
                content
            )

        except json.JSONDecodeError as error:

            raise ValueError(
                "LLM did not return valid JSON."
            ) from error

        return SemanticExtraction.model_validate(
            data
        )

    # ========================================================
    # CODE FENCE CLEANUP
    # ========================================================

    def _remove_code_fences(
        self,
        content: str,
    ) -> str:

        if not content.startswith(
            "```"
        ):
            return content.strip()

        lines = content.splitlines()

        if lines:
            lines = lines[1:]

        if (
            lines
            and lines[-1].strip() == "```"
        ):
            lines = lines[:-1]

        return "\n".join(
            lines
        ).strip()

    # ========================================================
    # FILTER ARTICLE TITLES / UI TEXT
    # ========================================================

    @staticmethod
    def _looks_like_article_title(
        text: str,
    ) -> bool:

        normalized = text.lower().strip()

        title_markers = [
            "travel guide",
            "things to do in",
            "best adventure experiences",
            "self-drive biking trip",
            "offbeat destinations",
            "holiday",
        ]

        return any(
            marker in normalized
            for marker in title_markers
        )

    # ========================================================
    # TEXT CLEANING
    # ========================================================

    @staticmethod
    def _clean_text(
        value,
    ) -> str:

        if value is None:
            return ""

        text = str(value).strip()

        # Repair common UTF-8/Latin-1 mojibake.
        if any(
            marker in text
            for marker in (
                "â€“",
                "â€”",
                "â€™",
                "â€œ",
                "â€",
                "â€¦",
            )
        ):
            try:
                text = text.encode(
                    "latin1"
                ).decode(
                    "utf-8"
                )
            except (
                UnicodeEncodeError,
                UnicodeDecodeError,
            ):
                pass

        return " ".join(
            text.split()
        )


# ============================================================
# MANALI TEST
# ============================================================

if __name__ == "__main__":

    from pathlib import Path

    from app.data_pipeline.dom_extractor import (
        DOMContentExtractor,
    )

    from app.data_pipeline.normalizer import (
        DataNormalizer,
    )

    input_path = Path(
        "data/raw/manali/manali.html"
    )

    html = input_path.read_text(
        encoding="utf-8",
        errors="ignore",
    )

    extractor = DOMContentExtractor()

    extracted_blocks = extractor.extract(
        html
    )

    normalizer = DataNormalizer()

    normalized_blocks = normalizer.normalize(
        extracted_blocks
    )

    semantic_extractor = SemanticExtractor()

    print(
        "\nRunning targeted semantic extraction..."
    )

    result = semantic_extractor.extract(
        normalized_blocks
    )

    print(
        "\nSEMANTIC EXTRACTION"
    )

    print(
        "=============================="
    )

    print(
        result.extraction.model_dump_json(
            indent=2
        )
    )

    print(
        "\nSource blocks sent to LLM:",
        len(result.source_blocks),
    )

    print(
        "Characters sent to LLM:",
        sum(
            len(
                semantic_extractor._clean_text(
                    block.content
                )
            )
            for block in result.source_blocks
        ),
    )