from dataclasses import dataclass

from bs4 import BeautifulSoup


@dataclass
class ExtractedSection:
    title: str
    content: str


class SectionExtractor:

    SECTION_ALIASES = {
        "activities": {
            "activities",
            "things to do",
            "adventure activities",
            "experiences",
        },
        "attractions": {
            "attractions",
            "places to visit",
            "tourist attractions",
            "tourist places",
        },
        "food": {
            "food",
            "local food",
            "cuisine",
            "what to eat",
        },
        "transport": {
            "transport",
            "how to reach",
            "getting there",
            "how to get there",
        },
        "stay": {
            "stay",
            "where to stay",
            "accommodation",
        },
        "weather": {
            "weather",
            "climate",
            "temperature",
        },
    }

    HEADING_TAGS = {
        "h1",
        "h2",
        "h3",
        "h4",
        "h5",
        "h6",
    }

    def extract(
        self,
        html: str,
    ) -> list[ExtractedSection]:

        if not html.strip():
            return []

        soup = BeautifulSoup(
            html,
            "html.parser",
        )

        sections = []

        headings = soup.find_all(
            self.HEADING_TAGS
        )

        for heading in headings:

            title = self._normalize_title(
                heading.get_text(
                    " ",
                    strip=True,
                )
            )

            if title is None:
                continue

            content_lines = []

            for element in heading.find_all_next():

                if (
                    element.name
                    in self.HEADING_TAGS
                ):
                    break

                if element.name not in {
                    "p",
                    "li",
                    "dt",
                    "dd",
                }:
                    continue

                text = element.get_text(
                    " ",
                    strip=True,
                )

                text = " ".join(
                    text.split()
                )

                if text:
                    content_lines.append(
                        text
                    )

            content = self._deduplicate(
                content_lines
            )

            if not content:
                continue

            sections.append(
                ExtractedSection(
                    title=title,
                    content="\n".join(
                        content
                    ),
                )
            )

        return sections

    def _normalize_title(
        self,
        title: str,
    ) -> str | None:

        normalized = (
            title
            .strip()
            .lower()
            .rstrip(":")
        )

        for (
            section_name,
            aliases,
        ) in self.SECTION_ALIASES.items():

            if normalized in aliases:
                return section_name

        return None

    def _deduplicate(
        self,
        lines: list[str],
    ) -> list[str]:

        result = []

        for line in lines:

            if (
                not result
                or line != result[-1]
            ):
                result.append(line)

        return result
 
