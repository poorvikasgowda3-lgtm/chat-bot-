import os
import json

import requests
import streamlit as st

st.set_page_config(
    page_title="PDF AI Assistant | RAG QA Chatbot",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
        .main .block-container {
            padding-top: 2rem;
            padding-bottom: 3rem;
            max-width: 1180px;
        }

        .app-shell {
            background: linear-gradient(180deg, rgba(15, 23, 42, 0.98), rgba(15, 23, 42, 0.96));
            border-radius: 18px;
            padding: 1.25rem;
            border: 1px solid rgba(148, 163, 184, 0.18);
        }

        .header-card {
            background: linear-gradient(135deg, #4f46e5, #7c3aed, #a855f7);
            color: white;
            border-radius: 20px;
            padding: 1.5rem 2rem;
            margin-bottom: 1.5rem;
            box-shadow: 0 18px 40px rgba(79, 70, 229, 0.35);
        }

        .header-card h1 {
            margin: 0;
            font-size: 2.4rem;
            font-weight: 800;
            color: white !important;
        }

        .header-card p {
            margin: 0.5rem 0 0;
            color: rgba(255,255,255,0.9);
            font-size: 1.02rem;
        }

        .info-card {
            background: rgba(15, 23, 42, 0.72);
            border: 1px solid rgba(148, 163, 184, 0.18);
            border-radius: 16px;
            padding: 1rem 1.1rem;
            height: 100%;
        }

        .metric-title {
            font-size: 0.8rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            opacity: 0.7;
            margin-bottom: 0.45rem;
        }

        .metric-value {
            font-size: 1.5rem;
            font-weight: 700;
            color: #f8fafc;
        }

        .status-badge {
            display: inline-block;
            padding: 0.45rem 0.8rem;
            border-radius: 999px;
            font-size: 0.8rem;
            font-weight: 700;
        }

        .status-active {
            background: rgba(34, 197, 94, 0.15);
            color: #bbf7d0;
            border: 1px solid rgba(34, 197, 94, 0.3);
        }

        .status-inactive {
            background: rgba(239, 68, 68, 0.12);
            color: #fecaca;
            border: 1px solid rgba(239, 68, 68, 0.3);
        }

        .citation-card {
            background: rgba(30, 41, 59, 0.9);
            border-left: 4px solid #8b5cf6;
            border-radius: 12px;
            padding: 0.9rem 1rem;
            margin-top: 0.45rem;
            margin-bottom: 0.6rem;
            color: #e2e8f0;
            line-height: 1.5;
        }

        .stChatMessage {
            border-radius: 16px;
        }

        .stButton > button {
            border-radius: 12px;
            font-weight: 700;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

API_BASE_URL = os.getenv("BACKEND_API_URL", "http://localhost:8000")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "processed_pdf" not in st.session_state:
    st.session_state.processed_pdf = None
if "pdf_chunks_count" not in st.session_state:
    st.session_state.pdf_chunks_count = 0


def check_backend_health():
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=3)
        if response.status_code == 200:
            return response.json()
    except Exception:
        return None
    return None


def upload_pdf_to_backend(uploaded_file):
    try:
        files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
        return requests.post(f"{API_BASE_URL}/upload", files=files, timeout=120)
    except Exception:
        return None


def ask_question_api(question: str):
    try:
        payload = {"question": question, "top_k": 3}
        response = requests.post(
            f"{API_BASE_URL}/ask",
            data=json.dumps(payload),
            headers={"Content-Type": "application/json"},
            timeout=60,
        )
        if response.status_code == 200:
            return response.json()
        return None
    except Exception:
        return None


def render_citations(sources):
    if not sources:
        return
    with st.expander("📌 View Source Citations"):
        for source in sources:
            st.markdown(
                f"""
                <div class="citation-card">
                    <b>📄 File:</b> {source['pdf_filename']} | <b>Page {source['page_number']}</b> (Relevance Score: {source['score']})<br/>
                    <i>"{source['text_snippet']}"</i>
                </div>
                """,
                unsafe_allow_html=True,
            )


with st.sidebar:
    st.image("https://img.icons8.com/isometric/100/pdf.png", width=72)
    st.title("System Control")

    health_data = check_backend_health()
    if health_data:
        st.markdown(
            '<span class="status-badge status-active">🟢 Backend Connected</span>',
            unsafe_allow_html=True,
        )
        st.caption(f"**Embedding Model:** `{health_data.get('embedding_model')}`")
        st.caption(f"**LLM Model:** `{health_data.get('llm_model')}`")
        st.caption(f"**Vectors Indexed:** `{health_data.get('total_documents_indexed')}`")
    else:
        st.markdown(
            '<span class="status-badge status-inactive">🔴 Backend Offline</span>',
            unsafe_allow_html=True,
        )
        st.warning("Start the FastAPI backend on port 8000 to enable the PDF Q&A flow.")

    st.divider()

    st.subheader("Document Status")
    if st.session_state.processed_pdf:
        st.success(f"**Active PDF:** `{st.session_state.processed_pdf}`")
        st.info(f"**Chunks Stored:** {st.session_state.pdf_chunks_count}")
    else:
        st.info("No document loaded yet.")

    if st.button("🗑️ Clear Chat"):
        st.session_state.chat_history = []
        st.rerun()

st.markdown(
    """
    <div class="header-card">
        <h1>📄 PDF AI Assistant</h1>
        <p>Upload a PDF, index it in Qdrant, and ask intelligent questions about the document content.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(
        """
        <div class="info-card">
            <div class="metric-title">Status</div>
            <div class="metric-value">Ready</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with col2:
    st.markdown(
        f"""
        <div class="info-card">
            <div class="metric-title">Chunks</div>
            <div class="metric-value">{st.session_state.pdf_chunks_count}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with col3:
    st.markdown(
        f"""
        <div class="info-card">
            <div class="metric-title">Document</div>
            <div class="metric-value">{'Loaded' if st.session_state.processed_pdf else 'Waiting'}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.subheader("Upload and process a PDF")
col_upload, col_button = st.columns([4, 1])
with col_upload:
    uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"], help="Upload a readable PDF document")
with col_button:
    st.write(" ")
    st.write(" ")
    process_btn = st.button("🚀 Process PDF", type="primary", use_container_width=True, disabled=uploaded_file is None)

if uploaded_file and process_btn:
    with st.spinner("Processing the PDF and indexing it into Qdrant..."):
        response = upload_pdf_to_backend(uploaded_file)
        if response and response.status_code == 200:
            data = response.json()
            st.session_state.processed_pdf = data["filename"]
            st.session_state.pdf_chunks_count = data["total_chunks"]
            st.success(
                f"✅ {data['filename']} processed successfully. {data['total_pages']} pages indexed and {data['total_chunks']} chunks stored."
            )
        else:
            detail = response.json().get("detail", "Upload failed") if response is not None else "Could not reach the backend API."
            st.error(f"❌ Upload failed: {detail}")

st.divider()

st.subheader("Ask questions about your PDF")
if st.session_state.processed_pdf:
    st.info(f"💬 Active context: **{st.session_state.processed_pdf}**")
else:
    st.warning("⚠️ Upload and process a PDF to enable the chat panel.")

for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "sources" in message and message["sources"]:
            render_citations(message["sources"])

if prompt := st.chat_input(
    "Ask a question about the uploaded PDF...",
    disabled=st.session_state.processed_pdf is None,
):
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Retrieving information from the document and generating the answer..."):
            response_data = ask_question_api(prompt)
            if response_data:
                answer = response_data["answer"]
                sources = response_data.get("sources", [])

                st.markdown(answer)
                render_citations(sources)

                st.session_state.chat_history.append(
                    {"role": "assistant", "content": answer, "sources": sources}
                )
            else:
                error_text = "Sorry, I could not reach the backend QA service."
                st.error(error_text)
                st.session_state.chat_history.append({"role": "assistant", "content": error_text})
