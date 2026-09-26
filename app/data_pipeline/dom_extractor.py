from dataclasses import dataclass
import re

from bs4 import BeautifulSoup
from bs4.element import Tag


@dataclass
class ExtractedBlock:
    block_type: str
    content: str


class DOMContentExtractor:

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

    def extract(
        self,
        html: str,
    ) -> list[ExtractedBlock]:

        if not html.strip():
            return []

        soup = BeautifulSoup(
            html,
            "html.parser",
        )

        self._remove_structural_noise(
            soup
        )

        main = soup.find("main")

        if main is None:
            return []

        blocks: list[ExtractedBlock] = []

        # -----------------------------------------------------
        # 1. Structured information
        # -----------------------------------------------------

        blocks.extend(
            self._extract_transport(
                main
            )
        )

        blocks.extend(
            self._extract_monthly_data(
                main
            )
        )

        # -----------------------------------------------------
        # 2. Narrative content
        # -----------------------------------------------------

        blocks.extend(
            self._extract_meaningful_paragraphs(
                main
            )
        )

        # -----------------------------------------------------
        # 3. Lists
        # -----------------------------------------------------

        blocks.extend(
            self._extract_meaningful_lists(
                main
            )
        )

        return self._deduplicate(
            blocks
        )

    # =========================================================
    # STRUCTURAL CLEANUP
    # =========================================================

    def _remove_structural_noise(
        self,
        soup: BeautifulSoup,
    ) -> None:

        for tag in list(
            soup.find_all(
                self.REMOVE_TAGS
            )
        ):

            if tag.parent is not None:
                tag.decompose()

    # =========================================================
    # TRANSPORT
    # =========================================================

    def _extract_transport(
        self,
        main: Tag,
    ) -> list[ExtractedBlock]:

        blocks = []

        for element in main.select(
            ".data-list"
        ):

            text = self._clean_text(
                element.get_text(
                    " ",
                    strip=True,
                )
            )

            if not text:
                continue

            lower = text.lower()

            if (
                "nearest airport" in lower
                or "nearest railway" in lower
                or "nearest railway station"
                in lower
            ):

                blocks.append(
                    ExtractedBlock(
                        block_type="transport",
                        content=text,
                    )
                )

        return blocks

    # =========================================================
    # MONTHLY DATA
    # =========================================================

    def _extract_monthly_data(
        self,
        main: Tag,
    ) -> list[ExtractedBlock]:

        blocks = []

        month_pattern = re.compile(
            r"(January|February|March|April|May|June|"
            r"July|August|September|October|November|December)"
            r"\s+"
            r"(-?\d+(?:\.\d+)?)"
            r"\s*-\s*"
            r"(-?\d+(?:\.\d+)?)"
            r"\s*°?\s*C",
            re.IGNORECASE,
        )

        # Look for containers whose class/id indicates
        # monthly information.
        candidates = []

        for element in main.find_all(
            ["div", "section", "article"]
        ):

            classes = element.get(
                "class",
                [],
            )

            element_id = (
                element.get(
                    "id",
                    "",
                )
                or ""
            )

            identifier = (
                " ".join(classes)
                + " "
                + element_id
            ).lower()

            if (
                "monthly" not in identifier
                and "month" not in identifier
            ):
                continue

            candidates.append(
                element
            )

        for element in candidates:

            text = self._clean_text(
                element.get_text(
                    " ",
                    strip=True,
                )
            )

            matches = month_pattern.findall(
                text
            )

            for month, minimum, maximum in matches:

                blocks.append(
                    ExtractedBlock(
                        block_type="temperature",
                        content=(
                            f"{month}: "
                            f"{minimum} - "
                            f"{maximum} °C"
                        ),
                    )
                )

        return blocks

    # =========================================================
    # PARAGRAPHS
    # =========================================================

    def _extract_meaningful_paragraphs(
        self,
        main: Tag,
    ) -> list[ExtractedBlock]:

        blocks = []

        for paragraph in main.find_all(
            "p"
        ):

            text = self._clean_text(
                paragraph.get_text(
                    " ",
                    strip=True,
                )
            )

            if len(text) < 40:
                continue

            if self._looks_like_ui_text(
                text
            ):
                continue

            blocks.append(
                ExtractedBlock(
                    block_type="paragraph",
                    content=text,
                )
            )

        return blocks

    # =========================================================
    # LISTS
    # =========================================================

    def _extract_meaningful_lists(
        self,
        main: Tag,
    ) -> list[ExtractedBlock]:

        blocks = []

        for element in main.find_all(
            ["ul", "ol"]
        ):

            items = []

            for item in element.find_all(
                "li",
                recursive=False,
            ):

                text = self._clean_text(
                    item.get_text(
                        " ",
                        strip=True,
                    )
                )

                if not text:
                    continue

                if self._looks_like_ui_text(
                    text
                ):
                    continue

                items.append(
                    text
                )

            if len(items) < 2:
                continue

            blocks.append(
                ExtractedBlock(
                    block_type="list",
                    content="\n".join(
                        items
                    ),
                )
            )

        return blocks

    # =========================================================
    # UI TEXT FILTER
    # =========================================================

    def _looks_like_ui_text(
        self,
        text: str,
    ) -> bool:

        normalized = text.lower().strip()

        obvious_ui = {
            "share",
            "login",
            "signup",
            "sign up",
            "today",
            "monthly",
            "clear all",
            "show results",
            "remove filter item",
            "featured",
        }

        if normalized in obvious_ui:
            return True

        ui_phrases = [
            "please apply filter",
            "please enter the email",
            "password reset",
            "verification email",
            "you are being redirected",
            "uses cookies",
            "privacy policy",
            "terms of use",
        ]

        for phrase in ui_phrases:

            if phrase in normalized:
                return True

        return False

    # =========================================================
    # TEXT NORMALIZATION
    # =========================================================

    def _clean_text(
        self,
        text: str,
    ) -> str:

        return " ".join(
            text.split()
        )

    # =========================================================
    # DEDUPLICATION
    # =========================================================

    def _deduplicate(
        self,
        blocks: list[ExtractedBlock],
    ) -> list[ExtractedBlock]:

        seen = set()
        result = []

        for block in blocks:

            normalized = (
                block.content
                .strip()
                .lower()
            )

            key = (
                block.block_type,
                normalized,
            )

            if key in seen:
                continue

            seen.add(key)

            result.append(
                block
            )

        return result
 
