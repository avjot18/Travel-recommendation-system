 
import json
from pathlib import Path

from langchain_ollama import ChatOllama
from pydantic import ValidationError

from app.data_pipeline.extraction_schema import (
    ExtractedDestinationData,
)


class DestinationExtractor:

    def __init__(
        self,
        model_name: str = "qwen3:1.7b",
        chunk_size: int = 2500,
    ):

        self.llm = ChatOllama(
            model=model_name,
            temperature=0,
        )

        self.chunk_size = chunk_size

    # ---------------------------------------------------------
    # TEXT CHUNKING
    # ---------------------------------------------------------

    def _split_into_chunks(
        self,
        source_text: str,
    ) -> list[str]:

        lines = source_text.splitlines()

        chunks = []
        current_chunk = []
        current_length = 0

        for line in lines:

            line = line.strip()

            if not line:
                continue

            line_length = len(line)

            if (
                current_chunk
                and current_length + line_length
                > self.chunk_size
            ):
                chunks.append(
                    "\n".join(current_chunk)
                )

                current_chunk = []
                current_length = 0

            current_chunk.append(line)

            current_length += line_length + 1

        if current_chunk:
            chunks.append(
                "\n".join(current_chunk)
            )

        return chunks

    # ---------------------------------------------------------
    # PROMPT
    # ---------------------------------------------------------

    def _build_prompt(
        self,
        source_text: str,
    ) -> str:

        return f"""
You are a strict information extraction system.

Extract structured travel information ONLY from the
SOURCE TEXT supplied below.

The source text is the ONLY source of truth.

IMPORTANT RULES:

1. Use ONLY information explicitly supported by the source.
2. Do NOT use outside knowledge.
3. Do NOT use your pretrained/world knowledge.
4. Do NOT invent facts.
5. Do NOT estimate missing information.
6. Do NOT infer information that is not explicitly stated.
7. If information is missing or unsupported, return null or [].
8. Preserve the meaning of the source.
9. Paraphrasing is allowed only when the factual meaning
   remains unchanged.
10. Return ONLY valid JSON.
11. Do not return markdown.
12. Do not explain your answer.

EVIDENCE-ONLY EXTRACTION:

For every value you output, ask:

"Where exactly is this supported by the supplied source?"

If you cannot identify explicit supporting text,
DO NOT output the value.

TRAVELER TYPES:

Only extract explicit traveler labels such as:

- couples
- families
- solo travelers
- backpackers

Do NOT infer traveler types from activities.

For example:

"hiking enthusiasts"

does NOT automatically mean:

"hikers"

are a traveler type.

PACE:

Only extract pace when the source explicitly describes
the destination or experience as:

- slow
- relaxed
- fast-paced
- laid-back
- etc.

Do NOT infer pace from activities.

CROWD LEVEL:

Only extract crowd level when explicitly stated.

Do NOT infer crowd level from popularity,
season, or activity levels.

BEST MONTHS:

Only populate best_months when the source explicitly
identifies particular months as:

- best
- ideal
- preferred
- recommended

Do NOT infer best months from:

- temperature
- weather
- activities
- festivals
- general popularity

SEASON PROFILE:

Extract seasonal information only when explicitly stated.

If the source contains monthly temperatures,
you may extract those temperatures.

Do NOT convert temperature information into
travel recommendations.

ACTIVITIES:

Extract only activities explicitly mentioned.

Only provide a description if the source explicitly
provides information describing that activity.

Do NOT add facts from general knowledge.

Do NOT infer categories.

Only provide best_seasons when the source explicitly
associates the activity with particular seasons or months.

ATTRACTIONS:

Extract only attractions explicitly mentioned.

If the source only provides the attraction name:

description = null
search_tags = []

Only provide descriptions or tags when explicitly
supported by the source.

Do NOT generate tags from general knowledge.

FOOD:

Extract only food items explicitly mentioned.

If the source only names a food item:

description = null

Do NOT invent:

- ingredients
- preparation methods
- characteristics
- regional claims

STAY AREAS:

Only extract a place as a stay area when the source
explicitly presents or describes it as a place or
area to stay.

Do NOT convert every location mentioned into a stay area.

Only provide suitable_for when explicitly stated.

Only provide budget_tier when explicitly stated.

TRANSPORT:

Extract only transport information explicitly stated.

Do NOT infer transport options from geographic knowledge.

PROS AND CONS:

Only extract pros and cons when explicitly provided.

Do NOT convert general descriptions into pros or cons.

NOTES:

Only include information explicitly supported by the source.

DESCRIPTIONS:

Descriptions must contain only facts supported by the source.

Do not add factual details from your own knowledge.

Do not combine unrelated facts to create new claims.

TAGS AND CATEGORIES:

Do not generate semantic tags or categories from
your own knowledge.

Use only terminology supported by the source.

UNCERTAINTY:

When uncertain whether information is supported by
the source, leave it null or empty.

A sparse extraction is better than an incorrect extraction.

IMPORTANT:

This is only ONE CHUNK of a larger document.

Extract information present in THIS CHUNK only.

Do not assume that information exists outside this chunk.

EXTRACTION FIELDS:

- description
- traveler_types
- pace
- crowd_level
- best_months
- season_profile
- activities
- attractions
- food_highlights
- stay_areas
- transport
- pros
- cons
- notes

For activities:

{{
    "name": "...",
    "description": "...",
    "category": "...",
    "best_seasons": []
}}

For attractions:

{{
    "name": "...",
    "description": "...",
    "search_tags": []
}}

For food:

{{
    "name": "...",
    "description": "..."
}}

For stay areas:

{{
    "name": "...",
    "description": "...",
    "suitable_for": [],
    "budget_tier": "..."
}}

For transport:

{{
    "type": "...",
    "name": "..."
}}

For season_profile:

{{
    "month": "...",
    "temperature": "..."
}}

Return ONLY valid JSON matching the required schema.

SOURCE TEXT:

{source_text}
"""

    # ---------------------------------------------------------
    # SINGLE CHUNK EXTRACTION
    # ---------------------------------------------------------

    def _extract_chunk(
        self,
        chunk: str,
    ) -> ExtractedDestinationData:

        prompt = self._build_prompt(chunk)

        response = self.llm.invoke(prompt)

        raw_output = response.content.strip()

        # Remove accidental markdown fences
        if raw_output.startswith("```"):
            raw_output = (
                raw_output
                .replace("```json", "")
                .replace("```", "")
                .strip()
            )

        try:

            extracted_data = json.loads(
                raw_output
            )

        except json.JSONDecodeError as exc:

            raise ValueError(
                "Ollama returned invalid JSON."
            ) from exc

        # Normalize single stay-area objects
        # into a list.
        if isinstance(
            extracted_data.get("stay_areas"),
            dict,
        ):

            extracted_data["stay_areas"] = [
                extracted_data["stay_areas"]
            ]

        try:

            return ExtractedDestinationData.model_validate(
                extracted_data
            )

        except ValidationError as exc:

            raise ValueError(
                "Extracted chunk failed Pydantic validation."
            ) from exc

    # ---------------------------------------------------------
    # MERGING
    # ---------------------------------------------------------

    def _merge_results(
        self,
        results: list[ExtractedDestinationData],
    ) -> ExtractedDestinationData:

        merged = ExtractedDestinationData()

        for result in results:

            # -------------------------------------------------
            # DESCRIPTION
            # -------------------------------------------------

            if (
                not merged.description
                and result.description
            ):
                merged.description = result.description

            # -------------------------------------------------
            # LIST FIELDS
            # -------------------------------------------------

            merged.traveler_types.extend(
                result.traveler_types
            )

            merged.best_months.extend(
                result.best_months
            )

            merged.activities.extend(
                result.activities
            )

            merged.attractions.extend(
                result.attractions
            )

            merged.food_highlights.extend(
                result.food_highlights
            )

            merged.stay_areas.extend(
                result.stay_areas
            )

            merged.transport.extend(
                result.transport
            )

            # -------------------------------------------------
            # OPTIONAL SIMPLE FIELDS
            # -------------------------------------------------

            if (
                merged.pace is None
                and result.pace is not None
            ):
                merged.pace = result.pace

            if (
                merged.crowd_level is None
                and result.crowd_level is not None
            ):
                merged.crowd_level = result.crowd_level

            if (
                merged.pros is None
                and result.pros is not None
            ):
                merged.pros = result.pros

            elif result.pros:
                if merged.pros is None:
                    merged.pros = []

                merged.pros.extend(
                    result.pros
                )

            if (
                merged.cons is None
                and result.cons is not None
            ):
                merged.cons = result.cons

            elif result.cons:
                if merged.cons is None:
                    merged.cons = []

                merged.cons.extend(
                    result.cons
                )

            if (
                merged.notes is None
                and result.notes is not None
            ):
                merged.notes = result.notes

            # -------------------------------------------------
            # SEASON PROFILE
            # -------------------------------------------------

            merged.season_profile.extend(
                result.season_profile
            )

        # -----------------------------------------------------
        # REMOVE DUPLICATES
        # -----------------------------------------------------

        merged.traveler_types = list(
            dict.fromkeys(
                merged.traveler_types
            )
        )
 
    def extract(
        self,
        source_text: str,
    ) -> ExtractedDestinationData:

        if not source_text.strip():
            raise ValueError(
                "Source text cannot be empty."
            )

        chunks = self._split_into_chunks(
            source_text
        )

        print(
            f"\nSource characters: "
            f"{len(source_text)}"
        )

        print(
            f"Chunks created: "
            f"{len(chunks)}"
        )

        results = []

        for index, chunk in enumerate(
            chunks,
            start=1
        ):

            print(
                f"\nExtracting chunk "
                f"{index}/{len(chunks)}..."
            )

            result = self._extract_chunk(
                chunk
            )

            results.append(result)

            print(
                f"Chunk {index} complete."
            )

        print(
            "\nMerging extracted data..."
        )

        merged_result = self._merge_results(
            results
        )

        print(
            "Extraction complete."
        )

        return merged_result

    def extract_file(
        self,
        input_path: str,
    ) -> ExtractedDestinationData:

        input_file = Path(input_path)

        if not input_file.exists():
            raise FileNotFoundError(
                f"Source file not found: "
                f"{input_file}"
            )

        source_text = input_file.read_text(
            encoding="utf-8"
        )

        return self.extract(
            source_text
        )