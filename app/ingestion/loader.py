import json
from pathlib import Path

from langchain_core.documents import Document

from app.ingestion.document_builder import TravelDocumentBuilder


class TravelDatasetLoader:

    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        self.document_builder = TravelDocumentBuilder()

    def load(self) -> list[Document]:

        with self.file_path.open(
            "r",
            encoding="utf-8"
        ) as file:
            data = json.load(file)

        destination_documents = (
            self.document_builder
            .build_destination_documents(data["destinations"])
        )
        
        attraction_documents = (
            self.document_builder
            .build_attraction_documents(data["attractions"])
        )
        
        return destination_documents + attraction_documents

    