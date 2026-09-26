from pathlib import Path

from app.data_pipeline.section_extractor import (
    SectionExtractor,
)


INPUT_FILE = (
    "data/raw/manali/"
    "manali.html"
)


def main():

    input_file = Path(INPUT_FILE)

    html = input_file.read_text(
        encoding="utf-8",
        errors="ignore",
    )

    extractor = SectionExtractor()

    sections = extractor.extract(
        html
    )

    print(
        f"\nSections found: "
        f"{len(sections)}"
    )

    print(
        "\n=============================="
    )

    for section in sections:

        print(
            f"\n[{section.title}]"
        )

        print(
            section.content[:1000]
        )

        print(
            "\n------------------------------"
        )


if __name__ == "__main__":
    main()