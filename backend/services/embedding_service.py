import logging
from typing import List
from backend.config import settings

logger = logging.getLogger(__name__)

class EmbeddingService:
    def __init__(self):
        self.model_name = settings.EMBEDDING_MODEL
        self.openai_key = settings.OPENAI_API_KEY
        self.st_model = None

        # Check if using local sentence-transformers
        if not self.openai_key or "sentence-transformers" in self.model_name:
            try:
                from sentence_transformers import SentenceTransformer
                logger.info(f"Loading local SentenceTransformer model: {self.model_name}")
                self.st_model = SentenceTransformer(self.model_name)
                self.vector_dim = self.st_model.get_sentence_embedding_dimension()
            except Exception as e:
                logger.warning(f"Could not load SentenceTransformer ({e}). Falling back to dummy/OpenAI mode.")
                self.vector_dim = 384
        else:
            self.vector_dim = 1536  # standard for text-embedding-3-small or ada-002

    def get_dimension(self) -> int:
        return self.vector_dim

    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []

        if self.st_model:
            embeddings = self.st_model.encode(texts, convert_to_numpy=True)
            return embeddings.tolist()

        if self.openai_key:
            try:
                import openai
                client = openai.OpenAI(api_key=self.openai_key)
                response = client.embeddings.create(
                    input=texts,
                    model=self.model_name if "text-embedding" in self.model_name else "text-embedding-3-small"
                )
                return [data.embedding for data in response.data]
            except Exception as e:
                logger.error(f"OpenAI embedding generation error: {e}")
                raise e

        raise RuntimeError("No embedding provider available. Provide OPENAI_API_KEY or install sentence-transformers.")

embedding_service = EmbeddingService()
