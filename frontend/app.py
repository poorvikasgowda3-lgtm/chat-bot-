import json
import os
import uuid
from datetime import datetime

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
            background: linear-gradient(180deg, rgba(15, 23, 42, 0.96), rgba(15, 23, 42, 0.82));
            border: 1px solid rgba(148, 163, 184, 0.2);
            border-radius: 26px;
            padding: 1rem 0.9rem;
            backdrop-filter: blur(12px);
            box-shadow: 0 18px 36px rgba(15, 23, 42, 0.42);
        }

        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #020817 0%, #0b1120 100%);
            color: #f8fafc;
        }

        .stSidebar * {
            color: #f8fafc !important;
        }

        .stSidebar .stSelectbox label,
        .stSidebar .stTextInput label,
        .stSidebar .stRadio label,
        .stSidebar .stMarkdown p,
        .stSidebar .stCaption,
        .stSidebar .stSubheader,
        .stSidebar .stButton p,
        .stSidebar button,
        .stSidebar .stExpander {
            color: #f8fafc !important;
        }

        .stSidebar .stButton > button {
            background: rgba(30, 41, 59, 0.88) !important;
            border: 1px solid rgba(148, 163, 184, 0.2) !important;
            color: #f8fafc !important;
        }

        .stSidebar .stButton > button:hover {
            background: rgba(79, 70, 229, 0.35) !important;
            border-color: rgba(165, 180, 252, 0.45) !important;
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
            background: linear-gradient(180deg, rgba(15, 23, 42, 0.94), rgba(15, 23, 42, 0.74));
            border: 1px solid rgba(148, 163, 184, 0.14);
            border-radius: 30px;
            padding: 1.2rem 1.1rem 0.75rem;
            box-shadow: 0 22px 50px rgba(15, 23, 42, 0.42), inset 0 1px 0 rgba(255,255,255,0.04);
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
            background: rgba(15, 23, 42, 0.8);
            border: 1px solid rgba(148, 163, 184, 0.18);
            border-radius: 22px;
            padding: 1rem 1.1rem;
            margin-top: 0.5rem;
            margin-bottom: 1rem;
            box-shadow: 0 14px 28px rgba(15, 23, 42, 0.28);
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
            margin: 0.9rem 0;
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
            box-shadow: inset 0 1px 0 rgba(255,255,255,0.02), 0 8px 22px rgba(2, 6, 23, 0.2);
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

        .session-view {
            margin-top: 0.5rem;
        }

        .session-item {
            display: block;
            width: 100%;
            text-align: left;
            border-radius: 12px;
            padding: 0.5rem 0.65rem;
            background: rgba(15, 23, 42, 0.64);
            border: 1px solid rgba(148, 163, 184, 0.12);
            color: #f8fafc;
            margin-bottom: 0.35rem;
        }

        .session-item.active {
            background: rgba(99, 102, 241, 0.17);
            border-color: rgba(129, 140, 248, 0.4);
            box-shadow: inset 0 0 0 1px rgba(165, 180, 252, 0.12);
        }

        .stExpander {
            border: 1px solid rgba(148, 163, 184, 0.16);
            border-radius: 14px;
            background: linear-gradient(180deg, rgba(15, 23, 42, 0.66), rgba(15, 23, 42, 0.46));
        }

        .stExpander > div > div:first-child {
            color: #f8fafc !important;
            font-weight: 600;
        }

        .stRadio > div {
            gap: 0.5rem;
        }

        .stRadio > div label {
            background: rgba(15, 23, 42, 0.56);
            border: 1px solid rgba(148, 163, 184, 0.12);
            border-radius: 10px;
            padding: 0.35rem 0.7rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

API_BASE_URL = os.getenv("BACKEND_API_URL", "http://localhost:8000")
APP_STATE_PATH = os.path.join(os.path.dirname(__file__), "chat_history.json")


def get_now_iso():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def get_document_set_key(files):
    normalized = [str(item).strip() for item in (files or [])]
    return "|".join(sorted(normalized))


def build_default_chat_session(files=None, title=None):
    safe_files = [str(item) for item in (files or [])]
    if title is None:
        if safe_files:
            label = ", ".join(safe_files[:2])
            if len(safe_files) > 2:
                label = f"{label}, +{len(safe_files) - 2} more"
            title = f"Docs: {label}"
        else:
            title = "New chat"

    return {
        "id": str(uuid.uuid4()),
        "title": title,
        "created_at": get_now_iso(),
        "updated_at": get_now_iso(),
        "messages": [],
        "document_set_key": get_document_set_key(safe_files),
    }


def sanitize_session_title(prompt: str):
    text = " ".join(prompt.strip().split())
    if len(text) <= 28:
        return text or "New chat"
    return text[:28].rstrip() + "..."


def format_chat_export(messages):
    lines = []
    for entry in messages:
        role = "You" if entry.get("role") == "user" else "Assistant"
        lines.append(f"[{role}] {entry.get('content', '').strip()}")
        if "sources" in entry and entry.get("sources"):
            lines.append("Sources:")
            for source in entry["sources"]:
                lines.append(
                    f"- {source.get('pdf_filename')} | Page {source.get('page_number')} | {source.get('text_snippet', '').strip()}"
                )
        lines.append("")
    return "\n".join(lines).strip() + "\n"


def load_persisted_state():
    default_state = {
        "chat_sessions": [build_default_chat_session()],
        "current_session_id": None,
        "uploaded_files": [],
        "pdf_chunks_count": 0,
        "selected_model": "gpt-4o-mini",
    }

    if not os.path.exists(APP_STATE_PATH):
        return default_state

    try:
        with open(APP_STATE_PATH, "r", encoding="utf-8") as f:
            saved = json.load(f)
        if not isinstance(saved, dict):
            return default_state

        default_state.update(saved)
        if "chat_sessions" not in saved or not saved.get("chat_sessions"):
            legacy_history = saved.get("chat_history", [])
            if legacy_history:
                default_state["chat_sessions"] = [{
                    "id": str(uuid.uuid4()),
                    "title": "Imported chat",
                    "created_at": get_now_iso(),
                    "updated_at": get_now_iso(),
                    "messages": legacy_history,
                }]
            else:
                default_state["chat_sessions"] = [build_default_chat_session()]
        if not default_state.get("current_session_id"):
            default_state["current_session_id"] = default_state["chat_sessions"][0]["id"]
        return default_state
    except Exception:
        return default_state


def save_persisted_state():
    session_list = st.session_state.get("chat_sessions", [])
    current_id = st.session_state.get("current_session_id")
    if not session_list:
        session_list = [build_default_chat_session(st.session_state.get("uploaded_files", []))]
        st.session_state.chat_sessions = session_list
        current_id = session_list[0]["id"]
        st.session_state.current_session_id = current_id

    for session in session_list:
        if "document_set_key" not in session:
            files = session.get("uploaded_files", [])
            session["document_set_key"] = get_document_set_key(files)

    payload = {
        "chat_sessions": session_list,
        "current_session_id": current_id,
        "uploaded_files": st.session_state.get("uploaded_files", []),
        "pdf_chunks_count": st.session_state.get("pdf_chunks_count", 0),
        "selected_model": st.session_state.get("selected_model", "gpt-4o-mini"),
    }

    try:
        with open(APP_STATE_PATH, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)
    except Exception:
        pass


def get_active_session():
    sessions = st.session_state.get("chat_sessions", [])
    current_id = st.session_state.get("current_session_id")

    if not sessions:
        new_session = build_default_chat_session(st.session_state.get("uploaded_files", []))
        st.session_state.chat_sessions = [new_session]
        st.session_state.current_session_id = new_session["id"]
        return new_session

    active = next((s for s in sessions if s.get("id") == current_id), sessions[0])
    st.session_state.current_session_id = active["id"]
    return active


def sorted_sessions(sessions):
    return sorted(sessions, key=lambda s: s.get("updated_at", ""), reverse=True)


def ensure_session_for_uploaded_files():
    files = st.session_state.get("uploaded_files", [])
    current_key = get_document_set_key(files)
    sessions = st.session_state.get("chat_sessions", [])

    if not files:
        return

    for session in sessions:
        if session.get("document_set_key") == current_key:
            st.session_state.current_session_id = session["id"]
            st.session_state.chat_history = session.get("messages", [])
            return

    new_session = build_default_chat_session(files)
    sessions.append(new_session)
    st.session_state.chat_sessions = sessions
    st.session_state.current_session_id = new_session["id"]
    st.session_state.chat_history = []
    save_persisted_state()


persisted_state = load_persisted_state()

if "chat_sessions" not in st.session_state:
    st.session_state.chat_sessions = persisted_state.get("chat_sessions", [build_default_chat_session()])
if "current_session_id" not in st.session_state:
    st.session_state.current_session_id = persisted_state.get("current_session_id") or st.session_state.chat_sessions[0]["id"]
if "uploaded_files" not in st.session_state:
    st.session_state.uploaded_files = persisted_state.get("uploaded_files", [])
if "pdf_chunks_count" not in st.session_state:
    st.session_state.pdf_chunks_count = persisted_state.get("pdf_chunks_count", 0)
if "selected_model" not in st.session_state:
    st.session_state.selected_model = persisted_state.get("selected_model", "gpt-4o-mini")

if not st.session_state.chat_sessions:
    st.session_state.chat_sessions = [build_default_chat_session(st.session_state.get("uploaded_files", []))]
    st.session_state.current_session_id = st.session_state.chat_sessions[0]["id"]

ensure_session_for_uploaded_files()
st.session_state.chat_history = get_active_session().get("messages", [])


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

    st.session_state.selected_model = st.selectbox(
        "Model",
        ["gpt-4o-mini", "gpt-3.5-turbo", "Local RAG"],
        index=["gpt-4o-mini", "gpt-3.5-turbo", "Local RAG"].index(st.session_state.selected_model),
        help="Choose the model used for answer generation.",
    )
    save_persisted_state()

    st.markdown('<div class="new-chat-button">', unsafe_allow_html=True)
    if st.button("＋ New chat", use_container_width=True):
        new_session = build_default_chat_session(st.session_state.get("uploaded_files", []))
        st.session_state.chat_sessions.append(new_session)
        st.session_state.current_session_id = new_session["id"]
        st.session_state.chat_history = []
        save_persisted_state()
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    st.divider()
    st.subheader("Saved chats")
    current_doc_key = get_document_set_key(st.session_state.get("uploaded_files", []))
    chat_view = st.radio("View", ["All chats", "Current document set"], horizontal=True, index=0)

    displayed_sessions = sorted_sessions(st.session_state.get("chat_sessions", []))
    if chat_view == "Current document set":
        displayed_sessions = [
            session for session in displayed_sessions
            if session.get("document_set_key") == current_doc_key
        ]

    if displayed_sessions:
        with st.expander(f"{chat_view} ({len(displayed_sessions)})", expanded=True):
            for session in displayed_sessions:
                is_active = session["id"] == st.session_state.get("current_session_id")
                summary = session.get("title", "New chat")
                stamp = session.get("updated_at", "")
                btn_label = f"{summary} • {stamp}"
                col_switch, col_delete = st.columns([5, 1])
                with col_switch:
                    if st.button(btn_label, key=f"session_{session['id']}", use_container_width=True, type="secondary" if not is_active else "primary"):
                        st.session_state.current_session_id = session["id"]
                        st.session_state.chat_history = session.get("messages", [])
                        save_persisted_state()
                        st.rerun()
                with col_delete:
                    if st.button("✕", key=f"delete_{session['id']}", use_container_width=True):
                        if len(st.session_state.chat_sessions) > 1:
                            st.session_state.chat_sessions = [s for s in st.session_state.chat_sessions if s["id"] != session["id"]]
                            if st.session_state.current_session_id == session["id"]:
                                remaining = sorted_sessions(st.session_state.chat_sessions)
                                if remaining:
                                    st.session_state.current_session_id = remaining[0]["id"]
                                    st.session_state.chat_history = remaining[0].get("messages", [])
                            save_persisted_state()
                            st.rerun()
    else:
        st.caption("No chats in this view yet.")

    active_session = get_active_session()
    st.text_input(
        "Rename saved topic",
        value=active_session.get("title", "New chat"),
        key="manual_title_input",
    )
    if st.session_state.get("manual_title_input") != active_session.get("title", "New chat"):
        active_session["title"] = st.session_state.manual_title_input.strip() or "New chat"
        active_session["updated_at"] = get_now_iso()
        save_persisted_state()

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
        active_session = get_active_session()
        active_session["messages"] = []
        active_session["title"] = "New chat"
        active_session["updated_at"] = get_now_iso()
        st.session_state.chat_history = []
        save_persisted_state()
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
        ensure_session_for_uploaded_files()
        save_persisted_state()
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
active_session = get_active_session()
chat_title = active_session.get("title", "New chat")
if st.session_state.uploaded_files:
    active_context = ", ".join(st.session_state.uploaded_files)
    st.markdown(
        f"""
        <div class="chat-header">
            <div class="chat-header-icon">💬</div>
            <div class="chat-header-text">{chat_title}</div>
            <span class="conversation-pill">{active_context}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        f"""
        <div class="chat-header">
            <div class="chat-header-icon">💬</div>
            <div class="chat-header-text">{chat_title}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.warning("⚠️ Upload and process one or more PDF files to activate the chat panel.")

chat_export = format_chat_export(st.session_state.chat_history)
if chat_export:
    st.download_button(
        label="⬇️ Download chat",
        data=chat_export,
        file_name=f"{chat_title.lower().replace(' ', '_') or 'chat'}.txt",
        mime="text/plain",
        use_container_width=True,
    )

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
    active_session = get_active_session()
    if active_session.get("document_set_key") != get_document_set_key(st.session_state.get("uploaded_files", [])):
        ensure_session_for_uploaded_files()
        active_session = get_active_session()

    active_session["messages"].append({"role": "user", "content": prompt})
    active_session["updated_at"] = get_now_iso()
    if active_session.get("title") == "New chat":
        active_session["title"] = sanitize_session_title(prompt)
    st.session_state.chat_history = active_session["messages"]
    save_persisted_state()

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
            active_session["messages"].append({"role": "assistant", "content": answer, "sources": sources})
            active_session["updated_at"] = get_now_iso()
            st.session_state.chat_history = active_session["messages"]
            save_persisted_state()
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
            active_session["messages"].append({"role": "assistant", "content": error_text})
            active_session["updated_at"] = get_now_iso()
            st.session_state.chat_history = active_session["messages"]
            save_persisted_state()
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
