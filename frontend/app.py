import streamlit as st
import requests
import os
import json

# Page Config
st.set_page_config(
    page_title="PDF AI Assistant | RAG QA Chatbot",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling (Dark Mode & Premium UI Tokens)
st.markdown("""
<style>
    /* Global Container Styles */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1100px;
    }
    
    /* Header Styling */
    .app-header {
        background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%);
        padding: 1.5rem 2rem;
        border-radius: 12px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 4px 20px rgba(79, 70, 229, 0.25);
    }
    .app-header h1 {
        margin: 0;
        font-size: 2.2rem;
        font-weight: 700;
        color: #ffffff !important;
    }
    .app-header p {
        margin: 0.5rem 0 0 0;
        opacity: 0.9;
        font-size: 1.05rem;
    }

    /* Badge & Cards */
    .status-badge {
        display: inline-block;
        padding: 0.4rem 0.8rem;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    .status-active {
        background-color: #DEF7EC;
        color: #03543F;
        border: 1px solid #84E1BC;
    }
    .status-inactive {
        background-color: #FDE8E8;
        color: #9B1C1C;
        border: 1px solid #F8B4B4;
    }

    /* Citation Box */
    .citation-card {
        background-color: #1E293B;
        border-left: 4px solid #6366F1;
        padding: 0.8rem 1.2rem;
        border-radius: 0 8px 8px 0;
        margin-top: 0.5rem;
        margin-bottom: 0.5rem;
        color: #E2E8F0;
        font-size: 0.9rem;
    }

    /* Chat bubble styling */
    .stChatMessage {
        border-radius: 12px;
    }
</style>
""", unsafe_allow_html=True)

# Configuration & Backend URL
API_BASE_URL = os.getenv("BACKEND_API_URL", "http://localhost:8000")

# Initialize Session State Variables
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "processed_pdf" not in st.session_state:
    st.session_state.processed_pdf = None
if "pdf_chunks_count" not in st.session_state:
    st.session_state.pdf_chunks_count = 0

# --- Helper API Functions ---
def check_backend_health():
    try:
        res = requests.get(f"{API_BASE_URL}/health", timeout=3)
        if res.status_code == 200:
            return res.json()
    except Exception:
        return None
    return None

def upload_pdf_to_backend(uploaded_file):
    try:
        files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
        res = requests.post(f"{API_BASE_URL}/upload", files=files, timeout=120)
        return res
    except Exception as e:
        return None

def ask_question_api(question: str):
    try:
        payload = {"question": question, "top_k": 3}
        headers = {"Content-Type": "application/json"}
        res = requests.post(f"{API_BASE_URL}/ask", data=json.dumps(payload), headers=headers, timeout=60)
        if res.status_code == 200:
            return res.json()
    except Exception as e:
        return None
    return None

# --- SIDEBAR: Status & Settings ---
with st.sidebar:
    st.image("https://img.icons8.com/isometric/100/pdf.png", width=64)
    st.title("⚙️ System Control")
    
    health_data = check_backend_health()
    if health_data:
        st.markdown('<span class="status-badge status-active">🟢 Backend Connected</span>', unsafe_allow_html=True)
        st.caption(f"**Embedding Model:** `{health_data.get('embedding_model')}`")
        st.caption(f"**LLM Model:** `{health_data.get('llm_model')}`")
        st.caption(f"**Vectors Indexed:** `{health_data.get('total_documents_indexed')}`")
    else:
        st.markdown('<span class="status-badge status-inactive">🔴 Backend Offline</span>', unsafe_allow_html=True)
        st.warning("FastAPI backend is not running! Please start the backend service on port 8000.")

    st.divider()

    st.subheader("📋 Document Status")
    if st.session_state.processed_pdf:
        st.success(f"**Active Document:**\n`{st.session_state.processed_pdf}`")
        st.info(f"Total Chunks Stored: **{st.session_state.pdf_chunks_count}**")
    else:
        st.info("No document currently loaded.")

    if st.button("🗑️ Clear Chat History"):
        st.session_state.chat_history = []
        st.rerun()

# --- MAIN HEADER ---
st.markdown("""
<div class="app-header">
    <h1>📄 PDF AI Assistant</h1>
    <p>Upload any PDF document and ask questions to get precise, instant AI answers with exact source citations.</p>
</div>
""", unsafe_allow_html=True)

# --- SECTION 1: PDF UPLOAD & PROCESSING ---
st.subheader("1. Upload & Process PDF Document")
col1, col2 = st.columns([3, 1])

with col1:
    uploaded_file = st.file_uploader("Select a PDF file", type=["pdf"], help="Upload a readable text PDF file")

with col2:
    st.write(" ")
    st.write(" ")
    process_btn = st.button("🚀 Process PDF", use_container_width=True, type="primary", disabled=uploaded_file is None)

if uploaded_file and process_btn:
    with st.spinner("⏳ Extracting text, generating embeddings, and storing in Qdrant Vector DB..."):
        response = upload_pdf_to_backend(uploaded_file)
        if response and response.status_code == 200:
            data = response.json()
            st.session_state.processed_pdf = data["filename"]
            st.session_state.pdf_chunks_count = data["total_chunks"]
            st.success(f"✅ **{data['filename']}** processed successfully! ({data['total_pages']} pages, {data['total_chunks']} chunks indexed in Qdrant)")
        else:
            err_msg = response.json().get("detail", "Error uploading file") if response else "Could not reach FastAPI backend."
            st.error(f"❌ Upload Failed: {err_msg}")

st.divider()

# --- SECTION 2: CHAT QUESTION PANEL ---
st.subheader("2. Ask Questions About Your PDF")

# Display status banner
if st.session_state.processed_pdf:
    st.info(f"💬 Active Context: Ready to answer questions from **{st.session_state.processed_pdf}**")
else:
    st.warning("⚠️ Please upload and process a PDF document above to start asking questions.")

# Render existing chat conversation
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "sources" in message and message["sources"]:
            with st.expander("📌 View Source Citations"):
                for src in message["sources"]:
                    st.markdown(f"""
                    <div class="citation-card">
                        <b>📄 File:</b> {src['pdf_filename']} | <b>Page {src['page_number']}</b> (Relevance Score: {src['score']})<br/>
                        <i>"{src['text_snippet']}"</i>
                    </div>
                    """, unsafe_allow_html=True)

# Chat Input Widget
if prompt := st.chat_input("Ask a question about your PDF document...", disabled=st.session_state.processed_pdf is None):
    # Add user message to state
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate bot response via API
    with st.chat_message("assistant"):
        with st.spinner("🔍 Retrieving top vectors from Qdrant & generating answer..."):
            res_data = ask_question_api(prompt)
            if res_data:
                answer = res_data["answer"]
                sources = res_data.get("sources", [])
                
                st.markdown(answer)
                
                if sources:
                    with st.expander("📌 View Source Citations"):
                        for src in sources:
                            st.markdown(f"""
                            <div class="citation-card">
                                <b>📄 File:</b> {src['pdf_filename']} | <b>Page {src['page_number']}</b> (Relevance Score: {src['score']})<br/>
                                <i>"{src['text_snippet']}"</i>
                            </div>
                            """, unsafe_allow_html=True)

                # Save assistant response to state
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": answer,
                    "sources": sources
                })
            else:
                err_text = "Sorry, I encountered an error communicating with the backend QA service."
                st.error(err_text)
                st.session_state.chat_history.append({"role": "assistant", "content": err_text})
