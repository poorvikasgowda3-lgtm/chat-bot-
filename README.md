# 📄 PDF AI Assistant — Full-Stack PDF Question-Answering Chatbot

A production-ready full-stack PDF Question-Answering application powered by **Streamlit** (Frontend), **FastAPI** (Backend REST API), **Qdrant** (Vector Database), and a **RAG (Retrieval-Augmented Generation)** pipeline.

---

## 🌟 Key Features

- **📄 Robust PDF Ingestion**: Extracts text page-by-page, cleans text, and generates overlapping chunks with page metadata.
- **⚡ Vector Search powered by Qdrant**: Efficient vector storage and retrieval. Supports both cloud/cluster Qdrant instances and local in-memory storage (`QDRANT_URL=:memory:`).
- **🧠 Flexible Embeddings & LLM**: Supports **OpenAI API** (`text-embedding-3-small`, `gpt-3.5-turbo`/`gpt-4o`) as well as **Local Sentence-Transformers** (`sentence-transformers/all-MiniLM-L6-v2`) for zero-cost offline testing.
- **💬 Conversational UI**: Interactive Streamlit chatbot UI displaying exact source citations and page references for every generated answer.
- **🐳 Docker Support**: Easily launch Qdrant, FastAPI backend, and Streamlit frontend using Docker Compose.

---

## 📁 Architecture & Project Structure

```
chat bot/
├── backend/
│   ├── main.py                     # FastAPI main app & CORS entrypoint
│   ├── config.py                   # Settings loader from .env
│   ├── models/
│   │   └── schemas.py              # Pydantic data schemas
│   ├── routes/
│   │   ├── health.py               # Health check endpoint (/health)
│   │   ├── upload.py               # PDF upload & indexing endpoint (/upload)
│   │   ├── question.py             # QA RAG query endpoint (/ask)
│   │   └── documents.py            # Collection metadata endpoint (/documents)
│   └── services/
│       ├── pdf_processor.py        # PDF text extraction & chunking
│       ├── embedding_service.py     # OpenAI / SentenceTransformers embeddings
│       ├── qdrant_service.py       # Qdrant collection setup & vector search
│       └── rag_service.py          # RAG context retrieval & answer synthesis
├── frontend/
│   └── app.py                      # Streamlit chat interface & backend consumer
├── .env.example                    # Sample environment file
├── .env                            # Active environment configuration
├── requirements.txt                # Dependencies
├── Dockerfile.backend              # Docker build file for FastAPI
├── Dockerfile.frontend             # Docker build file for Streamlit
├── docker-compose.yml              # Multi-container setup (Qdrant + FastAPI + Streamlit)
└── README.md                       # Complete documentation
```

---

## ⚙️ Configuration Variables (`.env`)

Configure your environment settings in `.env`:

```env
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000

# Optional: Add OpenAI key for full LLM natural language synthesis
OPENAI_API_KEY=

# Embedding model ('sentence-transformers/all-MiniLM-L6-v2' or 'text-embedding-3-small')
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# LLM model ('gpt-3.5-turbo', 'gpt-4o-mini', etc.)
LLM_MODEL=gpt-3.5-turbo

# Qdrant URL (Set to ':memory:' for instant local testing without Docker)
QDRANT_URL=:memory:
QDRANT_API_KEY=
QDRANT_COLLECTION_NAME=pdf_documents
```

---

## 🚀 Quickstart Guide

### Option 1: Running Locally (Recommended for Development)

1. **Install Python Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Start the FastAPI Backend**:
   ```bash
   python -m backend.main
   ```
   *The backend will run at `http://localhost:8000` (interactive API docs available at `http://localhost:8000/docs`).*

3. **Start the Streamlit Frontend**:
   Open a new terminal window/tab:
   ```bash
   streamlit run frontend/app.py
   ```
   *The frontend will launch automatically at `http://localhost:8501`.*

---

### Option 2: Running via Docker Compose

Run all three containers (Qdrant DB, FastAPI backend, Streamlit UI) in one command:

```bash
docker-compose up --build
```

Access points:
- **Streamlit App**: `http://localhost:8501`
- **FastAPI API**: `http://localhost:8000`
- **Qdrant Dashboard**: `http://localhost:6333/dashboard`

### Access from another device

`localhost` always means "this device", so `http://localhost:8501` will not open the app on a different computer or phone.

For devices connected to the same Wi-Fi network, start both services on all interfaces:

```powershell
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
streamlit run frontend/app.py --server.address 0.0.0.0 --server.port 8501
```

Then open the computer's LAN address from the other device, for example:

```text
http://192.168.0.103:8501
```

The LAN address can change when the computer reconnects to Wi-Fi. This address works only on the same network. For access from any location or mobile network, deploy the Docker Compose stack to a public server or place it behind a secure HTTPS tunnel and use the generated public URL.

---

## 🧪 Testing the RAG Pipeline

1. Open Streamlit at `http://localhost:8501`.
2. Ensure the sidebar indicates **🟢 Backend Connected**.
3. Upload any PDF file (e.g. sample documentation or report) and click **🚀 Process PDF**.
4. Once processed, ask questions in the chat panel at the bottom.
5. Expand **📌 View Source Citations** under any response to see the exact text snippet and page number retrieved from Qdrant.
