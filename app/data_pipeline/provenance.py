from dataclasses import dataclass, field
from datetime import datetime, timezone

from app.data_pipeline.normalizer import NormalizedBlock


@dataclass
class SourceMetadata:
    source_name: str
    source_url: str
    retrieved_at: str
    source_type: str


@dataclass
class ProvenancedBlock:
    block_type: str
    content: object
    source: SourceMetadata


class ProvenanceAttacher:

    def __init__(
        self,
        source_name: str,
        source_url: str,
        source_type: str = "web_page",
        retrieved_at: str | None = None,
    ):

        self.source = SourceMetadata(
            source_name=source_name,
            source_url=source_url,
            retrieved_at=(
                retrieved_at
                or self._current_timestamp()
            ),
            source_type=source_type,
        )

    def attach(
        self,
        blocks: list[NormalizedBlock],
    ) -> list[ProvenancedBlock]:

        provenanced_blocks = []

        for block in blocks:

            provenanced_blocks.append(
                ProvenancedBlock(
                    block_type=block.block_type,
                    content=block.content,
                    source=self.source,
                )
            )

        return provenanced_blocks

    @staticmethod
    def _current_timestamp() -> str:

        return datetime.now(
            timezone.utc
        ).isoformat()


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

    attacher = ProvenanceAttacher(
        source_name="Incredible India - Manali",
        source_url=(
            "https://www.incredibleindia.gov.in/"
            "en/himachal-pradesh/manali"
        ),
        source_type="official_tourism_page",
    )

    provenanced_blocks = attacher.attach(
        normalized_blocks
    )

    print(
        f"Normalized blocks: "
        f"{len(normalized_blocks)}"
    )

    print(
        f"Provenanced blocks: "
        f"{len(provenanced_blocks)}"
    )

    print(
        "\n=============================="
    )

    for index, block in enumerate(
        provenanced_blocks[:5],
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
            f"SOURCE: {block.source.source_name}"
        )

        print(
            f"URL: {block.source.source_url}"
        )

        print(
            f"RETRIEVED: {block.source.retrieved_at}"
        )

        print(
            "\n------------------------------"
        )