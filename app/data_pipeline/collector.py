import json
import time
from pathlib import Path

import requests


MANIFEST_PATH = Path(
    "data/source_manifest.json"
)

RAW_DIR = Path(
    "data/raw"
)


class SourceCollector:

    def __init__(
        self,
        manifest_path: Path = MANIFEST_PATH,
        raw_dir: Path = RAW_DIR,
        timeout: int = 30,
        delay_seconds: float = 1.0,
    ):
        self.manifest_path = manifest_path
        self.raw_dir = raw_dir
        self.timeout = timeout
        self.delay_seconds = delay_seconds

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

    # =========================================================
    # MANIFEST
    # =========================================================

    def load_manifest(self) -> list[dict]:

        if not self.manifest_path.exists():
            raise FileNotFoundError(
                f"Manifest not found: "
                f"{self.manifest_path}"
            )

        with self.manifest_path.open(
            "r",
            encoding="utf-8",
        ) as file:

            return json.load(file)

    # =========================================================
    # SAVE MANIFEST
    # =========================================================

    def save_manifest(
        self,
        manifest: list[dict],
    ) -> None:

        with self.manifest_path.open(
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                manifest,
                file,
                indent=2,
                ensure_ascii=False,
            )

    # =========================================================
    # DESTINATION DIRECTORY
    # =========================================================

    def _destination_directory(
        self,
        destination: dict,
    ) -> Path:

        destination_id = destination.get(
            "destination_id"
        )

        if not destination_id:
            raise ValueError(
                "Destination ID is missing."
            )

        return (
            self.raw_dir
            / destination_id
        )

    # =========================================================
    # RAW FILE
    # =========================================================

    def _raw_file_path(
        self,
        destination: dict,
    ) -> Path:

        directory = (
            self._destination_directory(
                destination
            )
        )

        return directory / "source.html"

    # =========================================================
    # DOWNLOAD
    # =========================================================

    def _download(
        self,
        url: str,
    ) -> str:

        response = self.session.get(
            url,
            timeout=self.timeout,
        )

        response.raise_for_status()

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

            raise ValueError(
                "Source did not return HTML. "
                f"Content-Type: {content_type}"
            )

        if not response.text.strip():

            raise ValueError(
                "Downloaded HTML is empty."
            )

        return response.text

    # =========================================================
    # COLLECT ONE SOURCE
    # =========================================================

    def collect_one(
        self,
        destination: dict,
        force: bool = False,
    ) -> str:

        url = destination.get(
            "source_url"
        )

        if not url:

            raise ValueError(
                "Source URL is missing."
            )

        output_path = (
            self._raw_file_path(
                destination
            )
        )

        # -----------------------------------------------------
        # CACHE
        # -----------------------------------------------------

        if (
            output_path.exists()
            and not force
        ):

            print(
                "CACHE HIT:",
                destination.get(
                    "destination_name"
                ),
            )

            return "cached"

        # -----------------------------------------------------
        # DOWNLOAD
        # -----------------------------------------------------

        print(
            "DOWNLOADING:",
            destination.get(
                "destination_name"
            ),
        )

        html = self._download(
            url
        )

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        output_path.write_text(
            html,
            encoding="utf-8",
        )

        print(
            "SAVED:",
            output_path,
        )

        return "downloaded"

    # =========================================================
    # COLLECT ALL
    # =========================================================

    def run(
        self,
        limit: int | None = None,
        force: bool = False,
    ) -> None:

        manifest = self.load_manifest()

        discovered = [
            item
            for item in manifest
            if item.get("status")
            == "discovered"
        ]

        if limit is not None:

            discovered = discovered[
                :limit
            ]

        downloaded = 0
        cached = 0
        failed = 0

        print(
            f"Sources available: "
            f"{len(discovered)}"
        )

        print(
            "=============================="
        )

        for index, destination in enumerate(
            discovered,
            start=1,
        ):

            name = destination.get(
                "destination_name"
            )

            print(
                f"\n"
                f"[{index}/{len(discovered)}] "
                f"{name}"
            )

            try:

                result = self.collect_one(
                    destination=destination,
                    force=force,
                )

                if result == "downloaded":
                    downloaded += 1

                elif result == "cached":
                    cached += 1

                if (
                    result == "downloaded"
                    and self.delay_seconds > 0
                ):
                    time.sleep(
                        self.delay_seconds
                    )

            except Exception as error:

                failed += 1

                print(
                    "FAILED:",
                    error,
                )

        print(
            "\n=============================="
        )

        print(
            f"Sources available: "
            f"{len(discovered)}"
        )

        print(
            f"Downloaded: "
            f"{downloaded}"
        )

        print(
            f"Cached: "
            f"{cached}"
        )

        print(
            f"Failed: "
            f"{failed}"
        )


if __name__ == "__main__":

    collector = SourceCollector()

    # Start with 5 destinations.
    # Remove the limit after verifying
    # the collector behaves correctly.
    collector.run(
        
    )