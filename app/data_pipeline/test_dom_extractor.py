from pathlib import Path

from app.data_pipeline.dom_extractor import (
    DOMContentExtractor,
)


INPUT_FILE = (
    "data/raw/manali/"
    "manali.html"
)


def main():

    html = Path(
        INPUT_FILE
    ).read_text(
        encoding="utf-8",
        errors="ignore",
    )

    extractor = DOMContentExtractor()

    blocks = extractor.extract(
        html
    )

    print(
        f"\nBlocks found: {len(blocks)}"
    )

    print(
        "\n=============================="
    )

    for index, block in enumerate(
        blocks,
        start=1,
    ):

        print(
            f"\nBLOCK {index}"
        )

        print(
            f"TYPE: {block.block_type}"
        )

        print(
            f"CONTENT:\n{block.content[:500]}"
        )

        print(
            "\n------------------------------"
        )


if __name__ == "__main__":
    main()