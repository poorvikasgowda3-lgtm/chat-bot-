import logging
import uuid
from typing import List, Dict, Any
from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels
from backend.config import settings
from backend.models.schemas import DocumentChunk
from backend.services.embedding_service import embedding_service

logger = logging.getLogger(__name__)

class QdrantService:
    def __init__(self):
        self.collection_name = settings.QDRANT_COLLECTION_NAME
        url = settings.QDRANT_URL
        api_key = settings.QDRANT_API_KEY if settings.QDRANT_API_KEY else None

        if not url or url == ":memory:":
            logger.info("Initializing in-memory Qdrant instance.")
            self.client = QdrantClient(":memory:")
        else:
            logger.info(f"Connecting to Qdrant cluster at {url}")
            self.client = QdrantClient(url=url, api_key=api_key)

        self._ensure_collection()

    def _ensure_collection(self):
        """Create Qdrant collection if it does not already exist."""
        try:
            collections = [c.name for c in self.client.get_collections().collections]
            if self.collection_name not in collections:
                vector_size = embedding_service.get_dimension()
                logger.info(f"Creating collection '{self.collection_name}' with vector size {vector_size}")
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=qmodels.VectorParams(
                        size=vector_size,
                        distance=qmodels.Distance.COSINE
                    )
                )
        except Exception as e:
            logger.error(f"Error checking/creating Qdrant collection: {e}")

    def insert_chunks(self, chunks: List[DocumentChunk], embeddings: List[List[float]]) -> bool:
        """Insert document chunks into Qdrant vector DB with metadata payload."""
        if not chunks or not embeddings:
            return False

        points = []
        for chunk, emb in zip(chunks, embeddings):
            # Generate deterministic or random UUID for Qdrant point ID
            point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, chunk.chunk_id))
            payload = {
                "chunk_id": chunk.chunk_id,
                "pdf_filename": chunk.pdf_filename,
                "page_number": chunk.page_number,
                "text": chunk.text
            }
            points.append(qmodels.PointStruct(
                id=point_id,
                vector=emb,
                payload=payload
            ))

        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )
        return True

    def search_similar(self, query_vector: List[float], top_k: int = 3) -> List[Dict[str, Any]]:
        """Search top_k similar chunks in Qdrant DB."""
        if hasattr(self.client, "query_points"):
            response = self.client.query_points(
                collection_name=self.collection_name,
                query=query_vector,
                limit=top_k
            )
            search_result = response.points
        elif hasattr(self.client, "search"):
            search_result = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                limit=top_k
            )
        else:
            search_result = []

        results = []
        for point in search_result:
            results.append({
                "score": getattr(point, "score", 0.0),
                "payload": getattr(point, "payload", {})
            })
        return results

    def get_document_count(self) -> int:
        """Count total vectors indexed in collection."""
        try:
            res = self.client.get_collection(collection_name=self.collection_name)
            return res.points_count or 0
        except Exception:
            return 0

qdrant_service = QdrantService()
