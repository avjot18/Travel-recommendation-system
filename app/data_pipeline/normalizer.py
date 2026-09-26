from dataclasses import dataclass
import re

from app.data_pipeline.dom_extractor import ExtractedBlock


@dataclass
class NormalizedTemperature:
    month: str
    minimum_celsius: float
    maximum_celsius: float


@dataclass
class NormalizedTransport:
    transport_type: str
    value: str


@dataclass
class NormalizedBlock:
    block_type: str
    content: object


class DataNormalizer:

    def normalize(
        self,
        blocks: list[ExtractedBlock],
    ) -> list[NormalizedBlock]:

        normalized = []

        for block in blocks:

            if block.block_type == "temperature":

                temperature = (
                    self._normalize_temperature(
                        block.content
                    )
                )

                if temperature is not None:
                    normalized.append(
                        NormalizedBlock(
                            block_type="temperature",
                            content=temperature,
                        )
                    )

            elif block.block_type == "transport":

                transport_blocks = (
                    self._normalize_transport(
                        block.content
                    )
                )

                normalized.extend(
                    transport_blocks
                )

            elif block.block_type == "paragraph":

                text = self._normalize_text(
                    block.content
                )

                if text:
                    normalized.append(
                        NormalizedBlock(
                            block_type="paragraph",
                            content=text,
                        )
                    )

            elif block.block_type == "list":

                items = self._normalize_list(
                    block.content
                )

                if items:
                    normalized.append(
                        NormalizedBlock(
                            block_type="list",
                            content=items,
                        )
                    )

            elif block.block_type == "key_value":

                key_value = (
                    self._normalize_key_value(
                        block.content
                    )
                )

                if key_value is not None:
                    normalized.append(
                        NormalizedBlock(
                            block_type="key_value",
                            content=key_value,
                        )
                    )

        return self._deduplicate(
            normalized
        )

    # =========================================================
    # TEMPERATURE
    # =========================================================

    def _normalize_temperature(
        self,
        text: str,
    ) -> NormalizedTemperature | None:

        pattern = re.compile(
            r"^\s*"
            r"(January|February|March|April|May|June|"
            r"July|August|September|October|November|December)"
            r"\s*:\s*"
            r"(-?\d+(?:\.\d+)?)"
            r"\s*-\s*"
            r"(-?\d+(?:\.\d+)?)"
            r"\s*°?\s*C"
            r"\s*$",
            re.IGNORECASE,
        )

        match = pattern.match(text)

        if not match:
            return None

        month = match.group(1).lower()

        minimum = float(
            match.group(2)
        )

        maximum = float(
            match.group(3)
        )

        if minimum > maximum:
            return None

        return NormalizedTemperature(
            month=month,
            minimum_celsius=minimum,
            maximum_celsius=maximum,
        )

    # =========================================================
    # TRANSPORT
    # =========================================================

    def _normalize_transport(
        self,
        text: str,
    ) -> list[NormalizedBlock]:

        normalized = []

        text = self._normalize_text(
            text
        )

        if not text:
            return normalized

        lower = text.lower()

        if "nearest airport" in lower:

            airport_value = re.sub(
                r"^nearest airports?\s*:\s*",
                "",
                text,
                flags=re.IGNORECASE,
            )

            normalized.append(
                NormalizedBlock(
                    block_type="transport",
                    content=NormalizedTransport(
                        transport_type="airport",
                        value=airport_value,
                    ),
                )
            )

        if (
            "nearest railway station" in lower
            or "nearest railway" in lower
        ):

            railway_value = re.sub(
                r"^nearest railway station\s*:\s*",
                "",
                text,
                flags=re.IGNORECASE,
            )

            railway_value = re.sub(
                r"^nearest railway\s*:\s*",
                "",
                railway_value,
                flags=re.IGNORECASE,
            )

            normalized.append(
                NormalizedBlock(
                    block_type="transport",
                    content=NormalizedTransport(
                        transport_type="railway_station",
                        value=railway_value,
                    ),
                )
            )

        return normalized

    # =========================================================
    # KEY / VALUE
    # =========================================================

    def _normalize_key_value(
        self,
        text: str,
    ) -> dict | None:

        match = re.match(
            r"^\s*([^:]{2,100})\s*:\s*(.+?)\s*$",
            text,
        )

        if not match:
            return None

        key = self._normalize_text(
            match.group(1)
        )

        value = self._normalize_text(
            match.group(2)
        )

        if not key or not value:
            return None

        return {
            "key": key,
            "value": value,
        }

    # =========================================================
    # LIST
    # =========================================================

    def _normalize_list(
        self,
        text: str,
    ) -> list[str]:

        items = []

        for line in text.splitlines():

            value = self._normalize_text(
                line
            )

            if value:
                items.append(
                    value
                )

        return self._deduplicate_strings(
            items
        )

    # =========================================================
    # TEXT
    # =========================================================

    def _normalize_text(
        self,
        text: str,
    ) -> str:

        return " ".join(
            text.split()
        ).strip()

    # =========================================================
    # DEDUPLICATION
    # =========================================================

    def _deduplicate(
        self,
        blocks: list[NormalizedBlock],
    ) -> list[NormalizedBlock]:

        seen = set()
        result = []

        for block in blocks:

            key = (
                block.block_type,
                repr(block.content).lower(),
            )

            if key in seen:
                continue

            seen.add(key)
            result.append(block)

        return result

    def _deduplicate_strings(
        self,
        values: list[str],
    ) -> list[str]:

        seen = set()
        result = []

        for value in values:

            key = value.lower()

            if key in seen:
                continue

            seen.add(key)
            result.append(value)

        return result


if __name__ == "__main__":

    from pathlib import Path

    from app.data_pipeline.dom_extractor import (
        DOMContentExtractor,
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

    print(
        f"Extracted blocks: "
        f"{len(extracted_blocks)}"
    )

    print(
        f"Normalized blocks: "
        f"{len(normalized_blocks)}"
    )

    print(
        "\n=============================="
    )

    for index, block in enumerate(
        normalized_blocks,
        start=1,
    ):

        print(
            f"\nBLOCK {index}"
        )

        print(
            f"TYPE: {block.block_type}"
        )

        print(
            f"CONTENT: {block.content}"
        )

        print(
            "\n------------------------------"
        )