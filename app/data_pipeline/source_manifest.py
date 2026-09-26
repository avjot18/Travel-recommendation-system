import json
from pathlib import Path


DATASET_PATH = Path(
    "data/india_travel_knowledge_base_v2_fully_populated.json"
)

OUTPUT_PATH = Path(
    "data/source_manifest.json"
)


class SourceManifestBuilder:

    def __init__(
        self,
        dataset_path: Path,
        output_path: Path,
    ):
        self.dataset_path = dataset_path
        self.output_path = output_path

    def load_destinations(self) -> list[dict]:

        if not self.dataset_path.exists():
            raise FileNotFoundError(
                f"Dataset not found: {self.dataset_path}"
            )

        with self.dataset_path.open(
            "r",
            encoding="utf-8",
        ) as file:

            data = json.load(file)

        return data.get(
            "destinations",
            []
        )

    def build(
        self,
        destinations: list[dict],
    ) -> list[dict]:

        manifest = []

        for destination in destinations:

            destination_id = destination.get(
                "destination_id"
            )

            name = destination.get(
                "name"
            )

            if not destination_id or not name:
                continue

            manifest.append(
    {
        "destination_id": destination_id,
        "destination_name": name,
        "state_or_ut": destination.get(
            "state_or_ut"
        ),
        "source_url": None,
        "source_name": None,
        "source_type": None,
        "status": "pending",
    }
)

        return manifest

    def save(
        self,
        manifest: list[dict],
    ) -> None:

        self.output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with self.output_path.open(
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                manifest,
                file,
                indent=2,
                ensure_ascii=False,
            )

    def run(self) -> None:

        destinations = (
            self.load_destinations()
        )

        manifest = self.build(
            destinations
        )

        self.save(
            manifest
        )

        print(
            f"Destinations found: "
            f"{len(destinations)}"
        )

        print(
            f"Manifest entries: "
            f"{len(manifest)}"
        )

        print(
            f"Output: {self.output_path}"
        )


if __name__ == "__main__":

    builder = SourceManifestBuilder(
        dataset_path=DATASET_PATH,
        output_path=OUTPUT_PATH,
    )

    builder.run()