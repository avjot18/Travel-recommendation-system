from pathlib import Path
from bs4 import BeautifulSoup


INPUT_FILE = (
    "data/raw/manali/"
    "manali.html"
)


html = Path(INPUT_FILE).read_text(
    encoding="utf-8",
    errors="ignore",
)

soup = BeautifulSoup(
    html,
    "html.parser",
)

main = soup.find("main")

print("MAIN FOUND:", main is not None)

if main:

    for element in main.find_all(
        ["div", "section", "article"],
        limit=100
    ):

        text = element.get_text(
            " ",
            strip=True
        )

        if text and len(text) < 300:

            print(
                "\nTAG:",
                element.name
            )

            print(
                "CLASS:",
                element.get("class")
            )

            print(
                "TEXT:",
                text[:250]
            )