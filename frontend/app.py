import json
import os

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
        html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"] {
            background: #020817;
            color: #e2e8f0;
        }

        .main .block-container {
            padding-top: 1.5rem;
            padding-bottom: 3rem;
            max-width: 1280px;
        }

        .top-header {
            background: linear-gradient(135deg, rgba(17, 24, 39, 0.96), rgba(49, 46, 129, 0.9), rgba(76, 29, 149, 0.9));
            border: 1px solid rgba(148, 163, 184, 0.18);
            border-radius: 22px;
            padding: 1.2rem 1.4rem;
            margin-bottom: 1.2rem;
            box-shadow: 0 20px 40px rgba(15, 23, 42, 0.65), 0 0 0 1px rgba(96, 165, 250, 0.12);
        }

        .top-header-row {
            display: flex;
            align-items: center;
            gap: 0.8rem;
        }

        .app-shell {
            max-width: 1180px;
            margin: 0 auto;
            width: 100%;
        }

        .sidebar-floating {
            background: rgba(15, 23, 42, 0.9);
            border: 1px solid rgba(148, 163, 184, 0.14);
            border-radius: 24px;
            padding: 1rem 0.9rem;
            backdrop-filter: blur(12px);
            box-shadow: 0 20px 40px rgba(15, 23, 42, 0.45);
        }

        .brand-badge {
            width: 2.4rem;
            height: 2.4rem;
            border-radius: 0.8rem;
            display: flex;
            align-items: center;
            justify-content: center;
            background: linear-gradient(135deg, #a78bfa, #5b8cff);
            box-shadow: 0 0 18px rgba(139, 92, 246, 0.5);
            font-size: 1.1rem;
        }

        .new-chat-button {
            margin-top: 0.5rem;
            width: 100%;
        }

        .new-chat-button > button {
            width: 100%;
            border-radius: 12px !important;
            background: linear-gradient(135deg, rgba(79,70,229,0.9), rgba(168,85,247,0.9)) !important;
            color: white !important;
            border: none !important;
            box-shadow: 0 0 20px rgba(124,58,237,0.3) !important;
        }

        .chat-canvas {
            background: linear-gradient(180deg, rgba(15, 23, 42, 0.9), rgba(15, 23, 42, 0.72));
            border: 1px solid rgba(148, 163, 184, 0.14);
            border-radius: 26px;
            padding: 1rem 1rem 0.75rem;
            box-shadow: 0 20px 45px rgba(15, 23, 42, 0.42);
            max-width: 980px;
            margin: 0 auto;
        }

        .conversation-pill {
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            background: rgba(99, 102, 241, 0.12);
            border: 1px solid rgba(129, 140, 248, 0.25);
            border-radius: 999px;
            padding: 0.45rem 0.8rem;
            color: #c4b5fd;
            font-size: 0.78rem;
            font-weight: 600;
        }

        .header-title {
            font-size: 1.35rem;
            font-weight: 700;
            color: white;
            letter-spacing: 0.01em;
        }

        .header-subtitle {
            margin-top: 0.3rem;
            color: rgba(226, 232, 240, 0.8);
            font-size: 0.9rem;
        }

        .stats-grid {
            margin-bottom: 1rem;
        }

        .info-card {
            background: rgba(15, 23, 42, 0.95);
            border: 1px solid rgba(148, 163, 184, 0.18);
            border-radius: 18px;
            padding: 0.9rem 1rem;
            height: 100%;
            box-shadow: 0 10px 28px rgba(15, 23, 42, 0.35);
        }

        .metric-title {
            font-size: 0.7rem;
            text-transform: uppercase;
            letter-spacing: 0.07em;
            opacity: 0.72;
            margin-bottom: 0.45rem;
            color: #cbd5e1;
        }

        .metric-value {
            font-size: 1.4rem;
            font-weight: 700;
            color: #f8fafc;
        }

        .tool-panel {
            background: rgba(15, 23, 42, 0.82);
            border: 1px solid rgba(148, 163, 184, 0.18);
            border-radius: 20px;
            padding: 1rem 1.1rem;
            margin-top: 0.5rem;
            margin-bottom: 1rem;
            box-shadow: 0 10px 25px rgba(15, 23, 42, 0.25);
        }

        .upload-box {
            background: rgba(15, 23, 42, 0.82);
            border: 1px solid rgba(148, 163, 184, 0.2);
            border-radius: 16px;
            padding: 0.8rem;
        }

        .status-badge {
            display: inline-block;
            padding: 0.45rem 0.8rem;
            border-radius: 999px;
            font-size: 0.76rem;
            font-weight: 700;
            margin-bottom: 0.7rem;
        }

        .status-active {
            background: rgba(34, 197, 94, 0.12);
            color: #bbf7d0;
            border: 1px solid rgba(34, 197, 94, 0.35);
        }

        .status-inactive {
            background: rgba(239, 68, 68, 0.12);
            color: #fecaca;
            border: 1px solid rgba(239, 68, 68, 0.35);
        }

        .chat-shell {
            background: rgba(15, 23, 42, 0.72);
            border: 1px solid rgba(148, 163, 184, 0.14);
            border-radius: 22px;
            padding: 1rem 1rem 0.5rem;
            box-shadow: inset 0 1px 0 rgba(255,255,255,0.04);
        }

        .chat-header {
            display: flex;
            align-items: center;
            gap: 0.8rem;
            margin-bottom: 0.9rem;
            padding: 0.3rem 0.2rem 0.8rem;
            border-bottom: 1px solid rgba(148, 163, 184, 0.12);
        }

        .chat-header-icon {
            width: 2rem;
            height: 2rem;
            border-radius: 0.7rem;
            display: flex;
            align-items: center;
            justify-content: center;
            background: linear-gradient(135deg, #f59e0b, #f97316);
            box-shadow: 0 0 18px rgba(249, 115, 22, 0.25);
        }

        .chat-header-text {
            font-weight: 700;
            color: #f8fafc;
            font-size: 1rem;
        }

        .message-row {
            display: flex;
            align-items: flex-start;
            gap: 0.65rem;
            margin: 0.8rem 0;
        }

        .avatar {
            width: 2rem;
            height: 2rem;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 0.9rem;
            font-weight: 700;
            flex-shrink: 0;
        }

        .avatar-user {
            background: linear-gradient(135deg, #fb7185, #f43f5e);
            box-shadow: 0 0 18px rgba(244, 63, 94, 0.35);
        }

        .avatar-assistant {
            background: linear-gradient(135deg, #fbbf24, #f59e0b);
            box-shadow: 0 0 18px rgba(245, 158, 11, 0.35);
            color: #111827;
        }

        .message-bubble {
            background: rgba(15, 23, 42, 0.9);
            border: 1px solid rgba(148, 163, 184, 0.14);
            border-radius: 18px;
            padding: 0.9rem 1rem;
            color: #f8fafc;
            line-height: 1.6;
            box-shadow: inset 0 1px 0 rgba(255,255,255,0.02);
        }

        .assistant-message {
            background: rgba(17, 24, 39, 0.9);
        }

        .user-message {
            background: rgba(31, 41, 55, 0.92);
        }

        .citation-card {
            background: rgba(15, 23, 42, 0.92);
            border-left: 4px solid #8b5cf6;
            border-radius: 12px;
            padding: 0.9rem 1rem;
            margin-top: 0.5rem;
            margin-bottom: 0.6rem;
            color: #e2e8f0;
            line-height: 1.5;
            border: 1px solid rgba(148, 163, 184, 0.16);
        }

        .stButton > button {
            border-radius: 12px;
            font-weight: 700;
            background: linear-gradient(135deg, #4f46e5, #7c3aed, #a855f7);
            color: white;
            border: none;
            box-shadow: 0 0 24px rgba(124, 58, 237, 0.3);
        }

        [data-testid="stFileUploaderDropzone"] {
            background: rgba(15, 23, 42, 0.82);
            border: 1px dashed rgba(129, 140, 248, 0.45);
            border-radius: 14px;
            color: #e2e8f0;
            box-shadow: 0 0 0 1px rgba(96, 165, 250, 0.08);
        }

        .stTextInput > div > div > input,
        .stTextArea > div > div > textarea {
            background: rgba(15, 23, 42, 0.92) !important;
            color: #f8fafc !important;
            border: 1px solid rgba(148, 163, 184, 0.2) !important;
            border-radius: 16px !important;
            box-shadow: 0 0 0 1px rgba(96, 165, 250, 0.15);
            padding: 0.9rem 1rem !important;
        }

        .stTextInput > div > div > input::placeholder,
        .stTextArea > div > div > textarea::placeholder {
            color: rgba(226, 232, 240, 0.58) !important;
        }

        .stChatInput {
            position: sticky;
            bottom: 1rem;
            background: rgba(2, 8, 23, 0.94);
            border: 1px solid rgba(148, 163, 184, 0.2);
            border-radius: 20px;
            box-shadow: 0 18px 34px rgba(15, 23, 42, 0.7), 0 0 0 1px rgba(96, 165, 250, 0.08);
            padding: 0.32rem 0.42rem;
            margin-top: 1rem;
        }

        .stChatInput textarea {
            background: rgba(15, 23, 42, 0.9) !important;
            color: #f8fafc !important;
            border-radius: 16px;
            padding: 0.9rem 1rem !important;
        }

        .stChatInput button {
            border-radius: 12px !important;
            background: linear-gradient(135deg, #4f46e5, #7c3aed, #a855f7) !important;
            color: white !important;
            border: none !important;
            box-shadow: 0 0 18px rgba(124, 58, 237, 0.35);
        }

        .sidebar-content {
            background: linear-gradient(180deg, #020817, #0b1220);
            border-right: 1px solid rgba(148, 163, 184, 0.12);
        }

        [data-testid="stSidebar"] {
            background: #020817;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

API_BASE_URL = os.getenv("BACKEND_API_URL", "http://localhost:8000")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "uploaded_files" not in st.session_state:
    st.session_state.uploaded_files = []
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


def upload_multiple_pdfs(file_list):
    uploaded = []
    failed = []
    total_chunks = 0

    for uploaded_file in file_list:
        response = upload_pdf_to_backend(uploaded_file)
        if response and response.status_code == 200:
            data = response.json()
            uploaded.append(data["filename"])
            total_chunks += int(data.get("total_chunks", 0))
        else:
            detail = response.json().get("detail", "Upload failed") if response is not None else "Could not reach the backend API."
            failed.append({"name": uploaded_file.name, "detail": detail})

    if uploaded:
        st.session_state.uploaded_files = list(dict.fromkeys(st.session_state.uploaded_files + uploaded))
        st.session_state.pdf_chunks_count = total_chunks

    return {"uploaded": uploaded, "failed": failed, "total_chunks": total_chunks}


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
    st.markdown('<div class="sidebar-floating">', unsafe_allow_html=True)
    st.image("https://img.icons8.com/isometric/100/pdf.png", width=72)
    st.title("Workspace")

    if "selected_model" not in st.session_state:
        st.session_state.selected_model = "gpt-4o-mini"

    st.session_state.selected_model = st.selectbox(
        "Model",
        ["gpt-4o-mini", "gpt-3.5-turbo", "Local RAG"],
        index=["gpt-4o-mini", "gpt-3.5-turbo", "Local RAG"].index(st.session_state.selected_model),
        help="Choose the model used for answer generation.",
    )

    st.markdown('<div class="new-chat-button">', unsafe_allow_html=True)
    if st.button("＋ New chat", use_container_width=True):
        st.session_state.chat_history = []
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    st.divider()
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
    st.subheader("Model Stats")
    st.metric("Available PDFs", len(st.session_state.uploaded_files))
    st.metric("Indexed Chunks", st.session_state.pdf_chunks_count)
    st.metric("Status", "Ready" if st.session_state.uploaded_files else "Waiting")

    st.divider()
    st.subheader("Uploaded Files")
    if st.session_state.uploaded_files:
        for item in st.session_state.uploaded_files:
            st.write(f"- {item}")
    else:
        st.info("No files uploaded yet.")

    st.divider()
    if st.button("🗑️ Clear Chat"):
        st.session_state.chat_history = []
        st.session_state.uploaded_files = []
        st.session_state.pdf_chunks_count = 0
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="app-shell">', unsafe_allow_html=True)

st.markdown(
    """
    <div class="top-header">
        <div class="top-header-row">
            <div class="brand-badge">✦</div>
            <div>
                <div class="header-title">PDF Research Assistant</div>
                <div class="header-subtitle">Upload up to 5 PDFs and ask questions across the full document set.</div>
            </div>
        </div>
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
            <div class="metric-title">Docs</div>
            <div class="metric-value">{len(st.session_state.uploaded_files)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with col3:
    st.markdown(
        f"""
        <div class="info-card">
            <div class="metric-title">Chunks</div>
            <div class="metric-value">{st.session_state.pdf_chunks_count}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown('<div class="tool-panel">', unsafe_allow_html=True)
col_upload, col_button = st.columns([5, 1])
with col_upload:
    uploaded_files = st.file_uploader(
        "Upload PDF files (up to 5)",
        type=["pdf"],
        accept_multiple_files=True,
        help="Upload up to five PDF documents for the assistant to search and answer across.",
    )
with col_button:
    st.write(" ")
    st.write(" ")
    selected_files = []
    process_btn = st.button(
        "🚀 Process PDFs",
        type="primary",
        use_container_width=True,
        disabled=not uploaded_files,
    )

if uploaded_files:
    selected_files = uploaded_files[:5]
    if len(uploaded_files) > 5:
        st.warning("Only the first 5 files were processed.")

if process_btn and selected_files:
    with st.spinner("Uploading and indexing the selected PDFs into Qdrant..."):
        result = upload_multiple_pdfs(selected_files)
        if result["uploaded"]:
            st.success(
                f"✅ Successfully processed: {', '.join(result['uploaded'])}. Total chunks indexed: {result['total_chunks']}"
            )
        if result["failed"]:
            for item in result["failed"]:
                st.error(f"❌ {item['name']}: {item['detail']}")

st.markdown('</div>', unsafe_allow_html=True)
st.divider()

st.markdown('<div class="chat-canvas">', unsafe_allow_html=True)
if st.session_state.uploaded_files:
    active_context = ", ".join(st.session_state.uploaded_files)
    st.markdown(
        f"""
        <div class="chat-header">
            <div class="chat-header-icon">💬</div>
            <div class="chat-header-text">Conversation</div>
            <span class="conversation-pill">{active_context}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        """
        <div class="chat-header">
            <div class="chat-header-icon">💬</div>
            <div class="chat-header-text">Conversation</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.warning("⚠️ Upload and process one or more PDF files to activate the chat panel.")

for message in st.session_state.chat_history:
    role = message["role"]
    avatar = "🧑‍💻" if role == "user" else "🤖"
    bubble_class = "user-message" if role == "user" else "assistant-message"

    with st.container():
        st.markdown(
            f"""
            <div class="message-row">
                <div class="avatar {'avatar-user' if role == 'user' else 'avatar-assistant'}">{avatar}</div>
                <div class="message-bubble {bubble_class}">{message['content']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if "sources" in message and message["sources"]:
            render_citations(message["sources"])

if prompt := st.chat_input(
    "Ask a question about the uploaded PDF(s)...",
    disabled=not st.session_state.uploaded_files,
):
    st.session_state.chat_history.append({"role": "user", "content": prompt})

    with st.container():
        st.markdown(
            f"""
            <div class="message-row">
                <div class="avatar avatar-user">🧑‍💻</div>
                <div class="message-bubble user-message">{prompt}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with st.spinner("Retrieving the best matches and generating the answer..."):
        response_data = ask_question_api(prompt)
        if response_data:
            answer = response_data["answer"]
            sources = response_data.get("sources", [])
            st.session_state.chat_history.append({"role": "assistant", "content": answer, "sources": sources})
            st.markdown(
                f"""
                <div class="message-row">
                    <div class="avatar avatar-assistant">🤖</div>
                    <div class="message-bubble assistant-message">{answer}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            render_citations(sources)
        else:
            error_text = "Sorry, I could not reach the backend QA service."
            st.session_state.chat_history.append({"role": "assistant", "content": error_text})
            st.markdown(
                f"""
                <div class="message-row">
                    <div class="avatar avatar-assistant">🤖</div>
                    <div class="message-bubble assistant-message">{error_text}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

st.markdown('</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)
