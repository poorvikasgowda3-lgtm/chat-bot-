from fastapi import APIRouter
from backend.services.qdrant_service import qdrant_service
from backend.services.embedding_service import embedding_service
from backend.config import settings
from backend.models.schemas import HealthResponse

router = APIRouter()

@router.get("/health", response_model=HealthResponse)
def health_check():
    doc_count = qdrant_service.get_document_count()
    return HealthResponse(
        status="healthy",
        qdrant_status="connected",
        embedding_model=settings.EMBEDDING_MODEL,
        llm_model=settings.LLM_MODEL,
        total_documents_indexed=doc_count
    )
