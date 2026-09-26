import json
import re
from pathlib import Path
from urllib.parse import quote

import requests


MANIFEST_PATH = Path(
    "data/source_manifest.json"
)

OUTPUT_PATH = Path(
    "data/source_manifest.json"
)


class IncredibleIndiaSourceResolver:

    BASE_URL = (
        "https://www.incredibleindia.gov.in/en"
    )

    STATE_SLUGS = {
        "Andaman and Nicobar Islands": "andaman-and-nicobar-islands",
        "Andhra Pradesh": "andhra-pradesh",
        "Arunachal Pradesh": "arunachal-pradesh",
        "Assam": "assam",
        "Bihar": "bihar",
        "Chandigarh": "chandigarh",
        "Chhattisgarh": "chhattisgarh",
        "Delhi": "delhi",
        "Goa": "goa",
        "Gujarat": "gujarat",
        "Haryana": "haryana",
        "Himachal Pradesh": "himachal-pradesh",
        "Jammu and Kashmir": "jammu-and-kashmir",
        "Jharkhand": "jharkhand",
        "Karnataka": "karnataka",
        "Kerala": "kerala",
        "Ladakh": "ladakh",
        "Madhya Pradesh": "madhya-pradesh",
        "Maharashtra": "maharashtra",
        "Manipur": "manipur",
        "Meghalaya": "meghalaya",
        "Mizoram": "mizoram",
        "Nagaland": "nagaland",
        "Odisha": "odisha",
        "Puducherry": "puducherry",
        "Punjab": "punjab",
        "Rajasthan": "rajasthan",
        "Sikkim": "sikkim",
        "Tamil Nadu": "tamil-nadu",
        "Telangana": "telangana",
        "Tripura": "tripura",
        "Uttar Pradesh": "uttar-pradesh",
        "Uttarakhand": "uttarakhand",
        "West Bengal": "west-bengal",
    }

    def __init__(
        self,
        timeout: int = 15,
    ):
        self.timeout = timeout

        self.session = requests.Session()

        self.session.headers.update(
            {
                "User-Agent": (
                    "ExploreEase/"
                    "1.0 "
                    "(travel research pipeline)"
                )
            }
        )

    def load_manifest(self) -> list[dict]:

        if not MANIFEST_PATH.exists():
            raise FileNotFoundError(
                f"Manifest not found: "
                f"{MANIFEST_PATH}"
            )

        with MANIFEST_PATH.open(
            "r",
            encoding="utf-8",
        ) as file:

            return json.load(file)

    def save_manifest(
        self,
        manifest: list[dict],
    ) -> None:

        with OUTPUT_PATH.open(
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                manifest,
                file,
                indent=2,
                ensure_ascii=False,
            )

    def slugify(
        self,
        value: str,
    ) -> str:

        value = value.lower().strip()

        value = value.replace(
            "&",
            "and",
        )

        value = re.sub(
            r"['’]",
            "",
            value,
        )

        value = re.sub(
            r"[^a-z0-9]+",
            "-",
            value,
        )

        return value.strip("-")

    def build_candidate_urls(
        self,
        destination_name: str,
        state_or_ut: str,
    ) -> list[str]:

        state_slug = self.STATE_SLUGS.get(
            state_or_ut
        )

        if not state_slug:
            state_slug = self.slugify(
                state_or_ut
            )

        destination_slug = self.slugify(
            destination_name
        )

        candidates = []

        # Primary destination-page pattern.
        candidates.append(
            (
                f"{self.BASE_URL}/"
                f"{state_slug}/"
                f"{destination_slug}"
            )
        )

        # Some destinations can have
        # alternative naming conventions.
        candidates.append(
            (
                f"{self.BASE_URL}/"
                f"{state_slug}/"
                f"{destination_slug}/"
            )
        )

        return list(
            dict.fromkeys(candidates)
        )

    def check_url(
        self,
        url: str,
    ) -> bool:

        try:

            response = self.session.get(
                url,
                timeout=self.timeout,
                allow_redirects=True,
            )

            if response.status_code != 200:
                return False

            content_type = (
                response.headers
                .get(
                    "content-type",
                    "",
                )
                .lower()
            )

            if (
                "text/html"
                not in content_type
            ):
                return False

            # Basic protection against
            # accepting an error page that
            # happens to return HTTP 200.
            text = response.text.lower()

            error_markers = [
                "page not found",
                "404 - not found",
                "404 not found",
                "content not available",
            ]

            for marker in error_markers:

                if marker in text:
                    return False

            return True

        except requests.RequestException:

            return False

    def resolve(
        self,
        destination: dict,
    ) -> dict:

        name = destination.get(
            "destination_name"
        )

        state = destination.get(
            "state_or_ut"
        )

        result = {
            **destination,
            "source_url": None,
            "source_name": None,
            "source_type": None,
            "status": "unresolved",
        }

        if not name or not state:
            result["status"] = (
                "missing_location"
            )

            return result

        candidates = (
            self.build_candidate_urls(
                destination_name=name,
                state_or_ut=state,
            )
        )

        for url in candidates:

            print(
                f"Checking: {name} → {url}"
            )

            if self.check_url(url):

                result[
                    "source_url"
                ] = url

                result[
                    "source_name"
                ] = "Incredible India"

                result[
                    "source_type"
                ] = (
                    "official_tourism"
                )

                result[
                    "status"
                ] = "discovered"

                return result

        return result

    def run(
        self,
        limit: int | None = None,
    ) -> None:

        manifest = self.load_manifest()

        if limit is not None:
            items = manifest[:limit]
        else:
            items = manifest

        resolved = []

        for index, destination in enumerate(
            items,
            start=1,
        ):

            print(
                f"\n"
                f"[{index}/{len(items)}] "
                f"{destination.get('destination_name')}"
            )

            result = self.resolve(
                destination
            )

            resolved.append(
                result
            )

            print(
                f"Status: "
                f"{result['status']}"
            )

        # If we ran a limited test,
        # update only those records.
        if limit is not None:

            remaining = manifest[
                limit:
            ]

            final_manifest = (
                resolved + remaining
            )

        else:

            final_manifest = resolved

        self.save_manifest(
            final_manifest
        )

        discovered = sum(
            1
            for item in final_manifest
            if item.get("status")
            == "discovered"
        )

        unresolved = sum(
            1
            for item in final_manifest
            if item.get("status")
            == "unresolved"
        )

        print(
            "\n=============================="
        )

        print(
            f"Total: {len(final_manifest)}"
        )

        print(
            f"Discovered: {discovered}"
        )

        print(
            f"Unresolved: {unresolved}"
        )


if __name__ == "__main__":

    resolver = (
        IncredibleIndiaSourceResolver()
    )

    # Start with only 10 destinations.
    # Once this behaves correctly,
    # remove the limit.
    resolver.run(
       
    )