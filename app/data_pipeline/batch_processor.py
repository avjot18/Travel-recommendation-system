import json
from pathlib import Path

from app.data_pipeline.dom_extractor import DOMContentExtractor
from app.data_pipeline.normalizer import DataNormalizer
from app.data_pipeline.provenance import ProvenanceAttacher
from app.data_pipeline.validator import DataValidator


MANIFEST_PATH = Path("data/source_manifest.json")
RAW_DIR = Path("data/raw")
OUTPUT_DIR = Path("data/staging")


class BatchProcessor:

    def __init__(self):
        self.extractor = DOMContentExtractor()
        self.normalizer = DataNormalizer()
        self.validator = DataValidator()

    def load_manifest(self):
        if not MANIFEST_PATH.exists():
            raise FileNotFoundError(
                f"Manifest not found: {MANIFEST_PATH}"
            )

        with MANIFEST_PATH.open("r", encoding="utf-8") as file:
            return json.load(file)

    def process_one(self, destination):
        destination_id = destination["destination_id"]
        destination_name = destination["destination_name"]
        source_url = destination["source_url"]

        input_path = RAW_DIR / destination_id / "source.html"
        output_path = OUTPUT_DIR / destination_id / "validated.json"

        if not input_path.exists():
            raise FileNotFoundError(
                f"Raw source not found: {input_path}"
            )

        # ---------------------------------------------------------
        # 1. Read raw HTML
        # ---------------------------------------------------------

        html = input_path.read_text(
            encoding="utf-8",
            errors="ignore",
        )

        # ---------------------------------------------------------
        # 2. Extract
        # ---------------------------------------------------------

        extracted_blocks = self.extractor.extract(html)

        # ---------------------------------------------------------
        # 3. Normalize
        # ---------------------------------------------------------

        normalized_blocks = self.normalizer.normalize(
            extracted_blocks
        )

        # ---------------------------------------------------------
        # 4. Validate
        # ---------------------------------------------------------

        validation_result = self.validator.validate(
            normalized_blocks
        )

        validated_blocks = validation_result.valid_blocks
        invalid_blocks = validation_result.invalid_blocks

        # ---------------------------------------------------------
        # 5. Attach provenance
        # ---------------------------------------------------------

        provenance_attacher = ProvenanceAttacher(
            source_name=f"Incredible India - {destination_name}",
            source_url=source_url,
            source_type="official_tourism_page",
        )

        provenanced_blocks = provenance_attacher.attach(
            validated_blocks
        )

        # ---------------------------------------------------------
        # 6. Serialize validated blocks
        # ---------------------------------------------------------

        serialized_blocks = []

        for block in provenanced_blocks:
            serialized_blocks.append(
                {
                    "block_type": block.block_type,
                    "content": self._serialize_content(
                        block.content
                    ),
                    "source": {
                        "source_name": block.source.source_name,
                        "source_url": block.source.source_url,
                        "retrieved_at": block.source.retrieved_at,
                        "source_type": block.source.source_type,
                    },
                }
            )

        # ---------------------------------------------------------
        # 7. Build staging document
        # ---------------------------------------------------------

        output = {
            "destination_id": destination_id,
            "destination_name": destination_name,
            "source_url": source_url,
            "blocks": serialized_blocks,
        }

        # ---------------------------------------------------------
        # 8. Save staging document
        # ---------------------------------------------------------

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        output_path.write_text(
            json.dumps(
                output,
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

        return {
            "destination_id": destination_id,
            "destination_name": destination_name,
            "extracted": len(extracted_blocks),
            "normalized": len(normalized_blocks),
            "validated": len(validated_blocks),
            "invalid": len(invalid_blocks),
            "output": str(output_path),
        }

    @staticmethod
    def _serialize_content(content):
        """
        Convert Pydantic models or dataclass-like objects
        into JSON-serializable data.
        """

        if hasattr(content, "model_dump"):
            return content.model_dump()

        if hasattr(content, "__dict__"):
            return content.__dict__

        return content

    def run(self):
        # ---------------------------------------------------------
        # Load manifest
        # ---------------------------------------------------------

        manifest = self.load_manifest()

        discovered = [
            item
            for item in manifest
            if item.get("status") == "discovered"
        ]

        total = len(discovered)

        print("=" * 60)
        print("BATCH PROCESSING")
        print("=" * 60)
        print(f"Sources available: {total}")

        # ---------------------------------------------------------
        # Counters
        # ---------------------------------------------------------

        processed = 0
        failed = 0

        total_extracted = 0
        total_normalized = 0
        total_validated = 0
        total_invalid = 0

        failures = []

        # ---------------------------------------------------------
        # Process every destination
        # ---------------------------------------------------------

        for index, destination in enumerate(
            discovered,
            start=1,
        ):
            destination_name = destination.get(
                "destination_name",
                "Unknown",
            )

            print(
                f"\n[{index}/{total}] {destination_name}"
            )

            try:
                result = self.process_one(
                    destination
                )

                processed += 1

                total_extracted += result["extracted"]
                total_normalized += result["normalized"]
                total_validated += result["validated"]
                total_invalid += result["invalid"]

                print(
                    f"  Extracted:  {result['extracted']}"
                )

                print(
                    f"  Normalized: {result['normalized']}"
                )

                print(
                    f"  Validated:  {result['validated']}"
                )

                print(
                    f"  Invalid:    {result['invalid']}"
                )

            except Exception as error:
                failed += 1

                failure = {
                    "destination_id": destination.get(
                        "destination_id"
                    ),
                    "destination_name": destination_name,
                    "error_type": type(error).__name__,
                    "error": str(error),
                }

                failures.append(failure)

                print(
                    f"  FAILED: {type(error).__name__}: {error}"
                )

        # ---------------------------------------------------------
        # Build batch report
        # ---------------------------------------------------------

        report = {
            "sources_available": total,
            "processed": processed,
            "failed": failed,
            "total_extracted": total_extracted,
            "total_normalized": total_normalized,
            "total_validated": total_validated,
            "total_invalid": total_invalid,
            "failures": failures,
        }

        # ---------------------------------------------------------
        # Save batch report
        # ---------------------------------------------------------

        OUTPUT_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

        report_path = OUTPUT_DIR / "batch_report.json"

        report_path.write_text(
            json.dumps(
                report,
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

        # ---------------------------------------------------------
        # Final summary
        # ---------------------------------------------------------

        print("\n" + "=" * 60)
        print("BATCH PROCESSING COMPLETE")
        print("=" * 60)

        print(
            f"Sources available: {total}"
        )

        print(
            f"Processed:         {processed}"
        )

        print(
            f"Failed:            {failed}"
        )

        print(
            f"Extracted blocks:  {total_extracted}"
        )

        print(
            f"Normalized blocks: {total_normalized}"
        )

        print(
            f"Validated blocks:  {total_validated}"
        )

        print(
            f"Invalid blocks:    {total_invalid}"
        )

        print(
            f"Report:            {report_path}"
        )


if __name__ == "__main__":
    processor = BatchProcessor()
    processor.run()