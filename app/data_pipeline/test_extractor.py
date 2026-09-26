import json

from app.data_pipeline.extractor import (
    DestinationExtractor
)


INPUT_FILE = (
    "data/cleaned/manali/"
    "incredible_india_manali.txt"
)


def main():

    extractor = DestinationExtractor()

    source_text = open(
        INPUT_FILE,
        encoding="utf-8"
    ).read()

    chunks = extractor._split_into_chunks(
        source_text
    )

    print(
        f"Total chunks: {len(chunks)}"
    )

    print(
        "Testing only chunk 1..."
    )

    result = extractor._extract_chunk(
        chunks[0]
    )

    print("\nEXTRACTED DATA")
    print("================")

    print(
        json.dumps(
            result.model_dump(),
            indent=2,
            ensure_ascii=False
        )
    )


if __name__ == "__main__":
    main()