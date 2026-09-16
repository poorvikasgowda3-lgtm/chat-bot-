from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class DocumentChunk(BaseModel):
    chunk_id: str
    pdf_filename: str
    page_number: int
    text: str

class UploadResponse(BaseModel):
    filename: str
    total_pages: int
    total_chunks: int
    status: str
    message: str

class QuestionRequest(BaseModel):
    question: str = Field(..., min_length=1, description="Question about the PDF content")
    top_k: Optional[int] = Field(default=3, description="Number of chunks to retrieve")

class SourceCitation(BaseModel):
    pdf_filename: str
    page_number: int
    chunk_id: str
    text_snippet: str
    score: float

class QuestionResponse(BaseModel):
    question: str
    answer: str
    sources: List[SourceCitation]
    found_in_doc: bool

class HealthResponse(BaseModel):
    status: str
    qdrant_status: str
    embedding_model: str
    llm_model: str
    total_documents_indexed: int
