from fastapi import APIRouter, HTTPException
from backend.models.schemas import QuestionRequest, QuestionResponse
from backend.services.rag_service import rag_service

router = APIRouter()

@router.post("/ask", response_model=QuestionResponse)
def ask_question(request: QuestionRequest):
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    try:
        response = rag_service.answer_question(request.question, top_k=request.top_k or 3)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error executing QA retrieval: {str(e)}")
