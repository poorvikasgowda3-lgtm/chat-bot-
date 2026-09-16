from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routes import health, upload, question, documents
from backend.config import settings

app = FastAPI(
    title="PDF QA Vector Search Backend API",
    description="FastAPI Backend for PDF Processing, Qdrant Vector Storage, and RAG Question Answering",
    version="1.0.0"
)

# Enable CORS for Streamlit Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(health.router, tags=["Health"])
app.include_router(upload.router, tags=["Upload"])
app.include_router(question.router, tags=["Question Answering"])
app.include_router(documents.router, tags=["Documents"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host=settings.BACKEND_HOST, port=settings.BACKEND_PORT, reload=True)
