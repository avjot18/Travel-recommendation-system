import json
from pathlib import Path

from app.data_pipeline.knowledge_builder import KnowledgeBuilder
from app.data_pipeline.dom_extractor import DOMContentExtractor
from app.data_pipeline.normalizer import DataNormalizer


DATASET_PATH = Path(
    "data/india_travel_knowledge_base_v2_fully_populated.json"
)

RAW_DIR = Path("data/raw")
OUTPUT_DIR = Path("data/production")
MANIFEST_PATH = Path("data/source_manifest.json")


class ProductionKnowledgeBuilder:

    def __init__(self):

        self.knowledge_builder = KnowledgeBuilder()

        self.dom_extractor = DOMContentExtractor()

        self.normalizer = DataNormalizer()

    # =========================================================
    # Load files
    # =========================================================

    def load_manifest(self):

        with MANIFEST_PATH.open(
            "r",
            encoding="utf-8",
        ) as file:
            return json.load(file)

    def load_dataset(self):

        with DATASET_PATH.open(
            "r",
            encoding="utf-8",
        ) as file:
            return json.load(file)

    # =========================================================
    # Serialize normalized blocks
    # =========================================================

    @staticmethod
    def serialize_content(content):

        if hasattr(
            content,
            "model_dump",
        ):
            return content.model_dump()

        if hasattr(
            content,
            "__dict__",
        ):
            return content.__dict__

        return content

    # =========================================================
    # Process one destination
    # =========================================================

    def process_one(
        self,
        destination,
        dataset,
    ):

        destination_id = destination[
            "destination_id"
        ]

        destination_name = destination[
            "destination_name"
        ]

        source_url = destination.get(
            "source_url"
        )

        raw_path = (
            RAW_DIR
            / destination_id
            / "source.html"
        )

        if not raw_path.exists():

            raise FileNotFoundError(
                f"Raw source missing: {raw_path}"
            )

        # -----------------------------------------------------
        # Read HTML
        # -----------------------------------------------------

        html = raw_path.read_text(
            encoding="utf-8",
            errors="ignore",
        )

        # -----------------------------------------------------
        # DOM extraction
        # -----------------------------------------------------

        extracted_blocks = (
            self.dom_extractor.extract(
                html
            )
        )

        # -----------------------------------------------------
        # Normalization
        # -----------------------------------------------------

        normalized_blocks = (
            self.normalizer.normalize(
                extracted_blocks
            )
        )

        # -----------------------------------------------------
        # Existing structured destination
        # -----------------------------------------------------

        existing_destination = (
            self.knowledge_builder.find_destination(
                dataset["destinations"],
                destination_id,
            )
        )

        if existing_destination is None:

            raise ValueError(
                f"Destination not found: "
                f"{destination_id}"
            )

        # -----------------------------------------------------
        # Build staging-compatible data
        # -----------------------------------------------------

        staging_data = {

            "destination_id":
                destination_id,

            "destination_name":
                destination_name,

            "source_url":
                source_url,

            "blocks": [
                {
                    "block_type":
                        block.block_type,

                    "content":
                        self.serialize_content(
                            block.content
                        ),

                    "source": {
                        "source_name":
                            f"Incredible India - "
                            f"{destination_name}",

                        "source_url":
                            source_url,

                        "source_type":
                            "official_tourism_page",
                    },
                }

                for block in normalized_blocks
            ],
        }

        # -----------------------------------------------------
        # Build deterministic profile
        # -----------------------------------------------------

        profile = (
            self.knowledge_builder.build_profile(
                existing_destination=
                    existing_destination,

                staging_data=
                    staging_data,
            )
        )

        return profile

    # =========================================================
    # Run batch
    # =========================================================

    def run(self):

        manifest = self.load_manifest()

        dataset = self.load_dataset()

        destinations = [
            item

            for item in manifest

            if item.get("status")
            == "discovered"
        ]

        total = len(destinations)

        processed = 0

        cached = 0

        failed = 0

        failures = []

        print("=" * 60)

        print(
            "FAST PRODUCTION KNOWLEDGE BUILD"
        )

        print("=" * 60)

        print(
            f"Destinations available: {total}"
        )

        for index, destination in enumerate(
            destinations,
            start=1,
        ):

            name = destination.get(
                "destination_name",
                "Unknown",
            )

            destination_id = destination.get(
                "destination_id"
            )

            output_path = (
                OUTPUT_DIR
                / destination_id
                / "profile.json"
            )

            print(
                f"\n[{index}/{total}] {name}"
            )

            # -------------------------------------------------
            # Resume
            # -------------------------------------------------

            if output_path.exists():

                cached += 1

                print(
                    "  CACHE HIT"
                )

                continue

            try:

                profile = self.process_one(
                    destination,
                    dataset,
                )

                output_path.parent.mkdir(
                    parents=True,
                    exist_ok=True,
                )

                output_path.write_text(
                    profile.model_dump_json(
                        indent=2
                    ),
                    encoding="utf-8",
                )

                processed += 1

                print(
                    f"  Activities: "
                    f"{len(profile.activities)}"
                )

                print(
                    f"  Attractions: "
                    f"{len(profile.attractions)}"
                )

                print(
                    f"  Food: "
                    f"{len(profile.food_highlights)}"
                )

                print(
                    f"  Seasons: "
                    f"{len(profile.season_profile or {})}"
                )

                print(
                    "  Saved"
                )

            except Exception as error:

                failed += 1

                failures.append(
                    {
                        "destination_id":
                            destination_id,

                        "destination_name":
                            name,

                        "error_type":
                            type(error).__name__,

                        "error":
                            str(error),
                    }
                )

                print(
                    f"  FAILED: "
                    f"{type(error).__name__}: "
                    f"{error}"
                )

        # =====================================================
        # Report
        # =====================================================

        OUTPUT_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

        report = {

            "destinations_available":
                total,

            "processed":
                processed,

            "cached":
                cached,

            "failed":
                failed,

            "failures":
                failures,
        }

        report_path = (
            OUTPUT_DIR
            / "production_build_report.json"
        )

        report_path.write_text(
            json.dumps(
                report,
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

        # =====================================================
        # Summary
        # =====================================================

        print("\n" + "=" * 60)

        print(
            "FAST PRODUCTION KNOWLEDGE BUILD COMPLETE"
        )

        print("=" * 60)

        print(
            f"Available: {total}"
        )

        print(
            f"Processed: {processed}"
        )

        print(
            f"Cached:    {cached}"
        )

        print(
            f"Failed:    {failed}"
        )

        print(
            f"Report:    {report_path}"
        )


if __name__ == "__main__":

    builder = ProductionKnowledgeBuilder()

    builder.run()