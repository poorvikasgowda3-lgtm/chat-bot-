from fastapi import APIRouter
from backend.services.qdrant_service import qdrant_service

router = APIRouter()

@router.get("/documents")
def get_documents_info():
    count = qdrant_service.get_document_count()
    return {
        "collection_name": qdrant_service.collection_name,
        "total_vector_chunks": count,
        "status": "ready" if count > 0 else "empty"
    }
