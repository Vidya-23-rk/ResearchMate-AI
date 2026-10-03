from sentence_transformers import SentenceTransformer


class EmbeddingService:

    def __init__(self):
        self.model = SentenceTransformer(
            "all-MiniLM-L6-v2"
        )

    def generate_embedding(self, text: str):
        """
        Convert one text chunk into an embedding vector.
        """
        return self.model.encode(
            text,
            convert_to_numpy=True
        )

    def generate_embeddings(self, texts: list[str]):
        """
        Convert multiple text chunks into embedding vectors.
        """
        return self.model.encode(
            texts,
            convert_to_numpy=True
        )


embedding_service = EmbeddingService()