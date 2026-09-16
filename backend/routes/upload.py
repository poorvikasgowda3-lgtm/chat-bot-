from fastapi import APIRouter, UploadFile, File, HTTPException
from backend.services.pdf_processor import pdf_processor
from backend.services.embedding_service import embedding_service
from backend.services.qdrant_service import qdrant_service
from backend.models.schemas import UploadResponse

router = APIRouter()

@router.post("/upload", response_model=UploadResponse)
async def upload_pdf(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Invalid file type. Only PDF files are supported.")

    try:
        content = await file.read()
        if len(content) == 0:
            raise HTTPException(status_code=400, detail="The uploaded PDF file is empty.")

        # 1. Process PDF & extract text chunks
        chunks = pdf_processor.process_pdf(content, file.filename)
        if not chunks:
            raise HTTPException(status_code=400, detail="No readable text could be extracted from the PDF.")

        # Determine total unique pages
        unique_pages = len(set(c.page_number for c in chunks))

        # 2. Generate embeddings for text chunks
        chunk_texts = [c.text for c in chunks]
        embeddings = embedding_service.generate_embeddings(chunk_texts)

        # 3. Store in Qdrant Vector Database
        qdrant_service.insert_chunks(chunks, embeddings)

        return UploadResponse(
            filename=file.filename,
            total_pages=unique_pages,
            total_chunks=len(chunks),
            status="success",
            message=f"PDF '{file.filename}' processed and {len(chunks)} chunks stored in Qdrant vector database."
        )

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process PDF: {str(e)}")
