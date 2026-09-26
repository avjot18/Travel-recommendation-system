from pathlib import Path
from bs4 import BeautifulSoup


class HTMLCleaner:

    REMOVE_TAGS = {
        "script",
        "style",
        "noscript",
        "svg",
        "canvas",
        "iframe",
        "form",
        "nav",
        "footer",
    }

    def clean(self, html: str) -> str:
        soup = BeautifulSoup(html, "html.parser")

        # Remove technical / boilerplate elements
        for tag in soup.find_all(self.REMOVE_TAGS):
            tag.decompose()

        # Prefer the actual page content
        # instead of the entire HTML body.
        content = soup.find("main")

        if content is None:
            content = soup.body

        if content is None:
            content = soup

        # Extract meaningful text while preserving
        # headings, paragraphs and list items.
        lines = []

        for element in content.find_all(
            ["h1", "h2", "h3", "h4", "h5", "h6",
             "p", "li", "dt", "dd"]
        ):

            text = element.get_text(
                " ",
                strip=True
            )

            text = " ".join(text.split())

            if text:
                lines.append(text)

        # Remove consecutive duplicates
        cleaned_lines = []

        for line in lines:
            if not cleaned_lines or line != cleaned_lines[-1]:
                cleaned_lines.append(line)

        return "\n".join(cleaned_lines)


class HTMLFileCleaner:

    def __init__(self):
        self.cleaner = HTMLCleaner()

    def clean_file(
        self,
        input_path: str,
        output_path: str
    ):

        input_file = Path(input_path)
        output_file = Path(output_path)

        if not input_file.exists():
            raise FileNotFoundError(
                f"Input file not found: {input_file}"
            )

        html = input_file.read_text(
            encoding="utf-8",
            errors="ignore"
        )

        cleaned_text = self.cleaner.clean(html)

        output_file.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        output_file.write_text(
            cleaned_text,
            encoding="utf-8"
        )

        print("HTML cleaning complete.")
        print("Input :", input_file)
        print("Output:", output_file)
        print("Characters:", len(cleaned_text))
        print("Lines:", len(cleaned_text.splitlines()))


if __name__ == "__main__":

    cleaner = HTMLFileCleaner()

    cleaner.clean_file(
        input_path="data/raw/manali/manali.html",
        output_path="data/cleaned/manali/incredible_india_manali.txt"
    )