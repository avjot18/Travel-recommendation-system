from langchain_huggingface import HuggingFaceEmbeddings


class EmbeddingService:

    def __init__(self, model_name: str):
        self.embeddings = HuggingFaceEmbeddings(
            model_name=model_name
        )

    def get_embeddings(self):
        return self.embeddings