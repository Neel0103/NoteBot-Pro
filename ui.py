"""Streamlit user interface for NoteBot Pro."""

from __future__ import annotations

from datetime import datetime
from typing import Any

import streamlit as st

import chat_manager
from llm import get_answer
from pdf_manager import process_pdfs
from utils import build_chat_export, html_text


def _theme() -> dict[str, Any]:
    dark = st.session_state.dark_mode

    return {
        "dark": dark,
        "background": "#0f1117" if dark else "#f8fafc",
        "card": "#1a1f2e" if dark else "#ffffff",
        "user_bubble": "#1e2433" if dark else "#e8f0fe",
        "bot_bubble": "#151c2c" if dark else "#ffffff",
        "border": "#2d3448" if dark else "#cbd5e1",
        "text": "#e2e8f0" if dark else "#1e293b",
        "subtext": "#8b9dc3" if dark else "#475569",
        "label": "#64748b" if dark else "#94a3b8",
        "accent": "#3b82f6" if dark else "#2563eb",
        "sidebar": "#0d1117" if dark else "#f1f5f9",
        "horizontal_rule": "#1f2937" if dark else "#e2e8f0",
        "empty": "#4b5563" if dark else "#94a3b8",
    }


def apply_styles(theme: dict[str, Any]) -> None:
    """Apply the original NoteBot Pro visual styling."""
    st.markdown(
        f"""
<style>
@import url(
    'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap'
);

html, body, [class*="css"] {{
    font-family: 'Inter', sans-serif;
}}

.main, .stApp {{
    background: {theme["background"]};
    color: {theme["text"]};
}}

.app-header {{
    background: linear-gradient(
        135deg,
        {theme["card"]},
        {theme["user_bubble"]}
    );
    border: 1px solid {theme["border"]};
    border-radius: 16px;
    padding: 20px 28px;
    margin-bottom: 20px;
    display: flex;
    align-items: center;
    justify-content: space-between;
}}

.app-title {{
    font-size: 1.8rem;
    font-weight: 700;
    color: {theme["text"]};
    margin: 0;
}}

.app-subtitle {{
    font-size: .875rem;
    color: {theme["subtext"]};
    margin: 4px 0 0;
}}

.mode-badge {{
    display: inline-block;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: .72rem;
    font-weight: 600;
    letter-spacing: .05em;
    text-transform: uppercase;
}}

.mode-pdf {{
    background: #1e3a5f;
    color: #60a5fa;
    border: 1px solid #2d5a9e;
}}

.mode-gen {{
    background: #1e3d2f;
    color: #4ade80;
    border: 1px solid #2d6b47;
}}

.chat-user {{
    background: {theme["user_bubble"]};
    border: 1px solid {theme["border"]};
    border-radius: 12px 12px 4px 12px;
    padding: 12px 16px;
    margin: 10px 0 10px 50px;
    color: {theme["text"]};
    font-size: .93rem;
    line-height: 1.6;
}}

.chat-bot {{
    background: {theme["bot_bubble"]};
    border: 1px solid {theme["border"]};
    border-left: 3px solid {theme["accent"]};
    border-radius: 4px 12px 12px 12px;
    padding: 12px 16px;
    margin: 10px 50px 10px 0;
    color: {theme["text"]};
    font-size: .93rem;
    line-height: 1.6;
}}

.chat-label {{
    font-size: .7rem;
    font-weight: 600;
    letter-spacing: .08em;
    text-transform: uppercase;
    margin-bottom: 6px;
    color: {theme["label"]};
}}

.source-box {{
    background: #0d1525;
    border: 1px solid #1e3a5f;
    border-radius: 8px;
    padding: 8px 12px;
    margin-top: 8px;
    font-size: .78rem;
    color: #60a5fa;
}}

[data-testid="stSidebar"] {{
    background-color: {theme["sidebar"]};
    border-right: 1px solid {theme["border"]};
}}

[data-testid="stSidebar"] * {{
    color: {theme["text"]};
}}

.stTextInput > div > div > input {{
    background-color: {theme["card"]} !important;
    color: {theme["text"]} !important;
    border: 1px solid {theme["border"]} !important;
    border-radius: 10px !important;
    font-size: .93rem !important;
    padding: 12px 16px !important;
}}

.stTextInput > div > div > input:focus {{
    border-color: {theme["accent"]} !important;
    box-shadow: 0 0 0 2px rgba(59, 130, 246, .2) !important;
}}

.stButton > button {{
    background: linear-gradient(
        135deg,
        {theme["accent"]},
        #1d4ed8
    );
    color: white;
    border: none;
    border-radius: 8px;
    padding: 8px 20px;
    font-weight: 600;
    font-size: .875rem;
    width: 100%;
    transition: all .2s;
}}

.stButton > button:hover {{
    opacity: .9;
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(59, 130, 246, .3);
}}

.stButton > button:disabled {{
    opacity: .72;
    transform: none;
    cursor: default;
}}

.info-card {{
    background: {theme["card"]};
    border: 1px solid {theme["border"]};
    border-radius: 10px;
    padding: 12px 16px;
    margin: 8px 0;
    font-size: .85rem;
    color: {theme["subtext"]};
}}

hr {{
    border-color: {theme["horizontal_rule"]} !important;
    margin: 14px 0 !important;
}}

.empty-state {{
    text-align: center;
    padding: 60px 20px;
    color: {theme["empty"]};
}}

.empty-state .icon {{
    font-size: 2.8rem;
    margin-bottom: 14px;
}}

.empty-state p {{
    font-size: .93rem;
    max-width: 340px;
    margin: 0 auto;
    line-height: 1.6;
}}

.stat-row {{
    display: flex;
    gap: 10px;
    margin: 10px 0;
    flex-wrap: wrap;
}}

.stat-pill {{
    background: {theme["card"]};
    border: 1px solid {theme["border"]};
    border-radius: 20px;
    padding: 4px 12px;
    font-size: .78rem;
    color: {theme["subtext"]};
}}

.stat-pill span {{
    color: {theme["accent"]};
    font-weight: 600;
}}

.edit-box {{
    background: {theme["card"]};
    border: 1px solid {theme["accent"]};
    border-radius: 10px;
    padding: 10px;
    margin: 6px 0 6px 50px;
}}

.session-item {{
    background: {theme["card"]};
    border: 1px solid {theme["border"]};
    border-radius: 8px;
    padding: 8px 12px;
    margin: 4px 0;
    font-size: .8rem;
    color: {theme["subtext"]};
    cursor: pointer;
}}
</style>
""",
        unsafe_allow_html=True,
    )


def _rerun() -> None:
    """Rerun Streamlit while supporting older compatible releases."""
    st.rerun()


def render_sidebar(theme: dict[str, Any]) -> str:
    """Render setup, live chats, PDFs, statistics, and chat controls."""
    with st.sidebar:
        st.markdown("## ⚙️ Setup")

        api_key = st.text_input(
            "Groq API Key",
            type="password",
            placeholder="gsk_...",
            help="Free at console.groq.com",
            key="groq_api_key",
        )

        st.markdown("---")

        theme_icon = "☀️" if theme["dark"] else "🌙"
        theme_label = "Light" if theme["dark"] else "Dark"

        if st.button(
            f"{theme_icon} Switch to {theme_label} Mode",
            key="theme_toggle",
        ):
            st.session_state.dark_mode = not st.session_state.dark_mode
            _rerun()

        st.markdown("---")

        if st.button("✏️ New Chat", key="new_chat"):
            chat_manager.create_chat()
            _rerun()

        visible_chats = [
            (chat_id, chat)
            for chat_id, chat in chat_manager.list_chats_newest_first()
            if chat.get("history")
        ]

        if visible_chats:
            st.markdown("**🕘 Past Chats:**")

            active_chat_id = chat_manager.get_active_chat_id()

            for chat_id, saved_chat in visible_chats:
                title = saved_chat.get("title", "New Chat")
                display_title = (
                    title
                    if len(title) <= 28
                    else title[:28].rstrip() + "…"
                )
                is_active = chat_id == active_chat_id
                prefix = "●" if is_active else "💬"

                title_column, delete_column = st.columns([5, 1])

                with title_column:
                    if st.button(
                        f"{prefix} {display_title}",
                        key=f"session_{chat_id}",
                        disabled=is_active,
                        help=title,
                    ):
                        chat_manager.switch_chat(chat_id)
                        _rerun()

                with delete_column:
                    if st.button(
                        "✕",
                        key=f"delete_{chat_id}",
                        help="Delete this chat",
                    ):
                        pending = st.session_state.get("pending_request")

                        if (
                            pending
                            and pending.get("chat_id") == chat_id
                        ):
                            st.session_state.pop(
                                "pending_request",
                                None,
                            )

                        chat_manager.delete_chat(chat_id)
                        _rerun()

        st.markdown("---")
        st.markdown("## 📂 Upload PDFs")
        st.markdown(
            """
<div class="info-card">
Upload PDFs then click <b>Process PDFs</b> to activate PDF search.
</div>
""",
            unsafe_allow_html=True,
        )

        active_chat_id = chat_manager.get_active_chat_id()

        uploaded_files = st.file_uploader(
            "Upload PDFs",
            type="pdf",
            accept_multiple_files=True,
            label_visibility="collapsed",
            key=f"pdf_upload_{active_chat_id}",
        )

        if uploaded_files and api_key:
            if st.button(
                "🔄 Process PDFs",
                key=f"process_pdfs_{active_chat_id}",
            ):
                try:
                    with st.spinner("Reading PDFs..."):
                        chunks, pdf_names = process_pdfs(
                            uploaded_files
                        )
                        chat_manager.set_pdf_state(
                            chunks,
                            pdf_names,
                        )

                    st.success(
                        f"✅ {len(pdf_names)} PDF(s) ready! "
                        f"({len(chunks)} chunks) — now ask questions!"
                    )
                except Exception as error:
                    st.error(
                        "Could not process the uploaded PDF files. "
                        f"{error}"
                    )

        active_chat = chat_manager.get_active_chat()

        st.sidebar.error(
            f"ACTIVE CHAT: {chat_manager.get_active_chat_id()} | "
            f"PDFs: {active_chat.get('pdf_names', [])} | "
            f"CHUNKS: {len(active_chat.get('pdf_chunks', []))}"
        )

        if active_chat["pdf_names"]:
            st.markdown("---")
            st.markdown("**📄 Loaded PDFs:**")

            for pdf_name in active_chat["pdf_names"]:
                safe_name = pdf_name.replace("`", "'")
                st.markdown(f"- `{safe_name}`")

        history = active_chat["history"]

        if history:
            st.markdown("---")

            pdf_answers = sum(
                1
                for entry in history
                if entry.get("role") == "bot"
                and entry.get("mode") == "pdf"
            )
            general_answers = sum(
                1
                for entry in history
                if entry.get("role") == "bot"
                and entry.get("mode") == "general"
            )
            question_count = sum(
                1
                for entry in history
                if entry.get("role") == "user"
            )

            st.markdown(
                f"""
<div class="stat-row">
    <div class="stat-pill">
        💬 <span>{question_count}</span> Q&As
    </div>
    <div class="stat-pill">
        📄 <span>{pdf_answers}</span> PDF
    </div>
    <div class="stat-pill">
        ✨ <span>{general_answers}</span> General
    </div>
</div>
""",
                unsafe_allow_html=True,
            )

            st.markdown("---")

            st.download_button(
                "⬇️ Download Chat",
                data=build_chat_export(history),
                file_name=(
                    "notebot_"
                    f"{datetime.now().strftime('%Y%m%d_%H%M')}.txt"
                ),
                mime="text/plain",
                key=f"download_{active_chat_id}",
            )

        st.markdown("---")

        clear_column, reset_column = st.columns(2)

        with clear_column:
            if st.button(
                "🗑️ Clear Chat",
                key=f"clear_{active_chat_id}",
            ):
                pending = st.session_state.get("pending_request")

                if (
                    pending
                    and pending.get("chat_id") == active_chat_id
                ):
                    st.session_state.pop("pending_request", None)

                chat_manager.clear_active_chat()
                _rerun()

        with reset_column:
            if st.button("🔃 Reset All", key="reset_all"):
                st.session_state.pop("pending_request", None)
                chat_manager.reset_all()
                _rerun()

        st.markdown("---")

        st.markdown(
            f"""
<div style="
    font-size: .75rem;
    color: {theme["label"]};
    line-height: 1.8;
">
    <b>How it works:</b><br>
    1. Enter Groq API key<br>
    2. Upload PDF → click Process PDFs<br>
    3. Ask anything!<br><br>
    ✏️ Edit any message → resends from there<br>
    🔵 <b style="color: #60a5fa;">Blue</b> = From PDF<br>
    🟢 <b style="color: #4ade80;">Green</b> = General AI
</div>
""",
            unsafe_allow_html=True,
        )

    return api_key


def render_header(theme: dict[str, Any]) -> None:
    """Render the main application header."""
    active_chat = chat_manager.get_active_chat()
    mode_text = "🌙 Dark" if theme["dark"] else "☀️ Light"

    st.markdown(
        f"""
<div class="app-header">
    <div>
        <p class="app-title">🤖 NoteBot Pro</p>
        <p class="app-subtitle">
            Ask from your PDFs — or ask anything.
            100% free, no downloads.
        </p>
    </div>
    <div style="
        font-size: .8rem;
        color: {theme["label"]};
        text-align: right;
    ">
        {mode_text} Mode<br>
        <span style="color: {theme["subtext"]};">
            {len(active_chat["pdf_names"])} PDF(s) loaded
        </span>
    </div>
</div>
""",
        unsafe_allow_html=True,
    )


def render_chat(api_key: str) -> None:
    """Render every message belonging to the active chat."""
    history = chat_manager.get_active_chat()["history"]

    if not history:
        st.markdown(
            """
<div class="empty-state">
    <div class="icon">💬</div>
    <p>
        Ask anything — from your PDFs or general knowledge.
        <br><br>
        <b>Tip:</b> Upload a PDF → click <b>Process PDFs</b>
        → then ask questions from it!
    </p>
</div>
""",
            unsafe_allow_html=True,
        )
        return

    for index, entry in enumerate(history):
        if entry.get("role") == "user":
            _render_user_message(index, entry, api_key)
        else:
            _render_bot_message(index, entry)


def _render_user_message(
    index: int,
    entry: dict[str, Any],
    api_key: str,
) -> None:
    """Render a user message or its edit form."""
    active_chat_id = chat_manager.get_active_chat_id()

    if st.session_state.editing_idx == index:
        new_text = st.text_input(
            "Edit your message:",
            value=st.session_state.edit_text,
            key=f"edit_input_{active_chat_id}_{index}",
        )

        resend_column, cancel_column = st.columns([1, 1])

        with resend_column:
            if st.button(
                "✅ Resend",
                key=f"resend_{active_chat_id}_{index}",
            ):
                if not api_key.strip():
                    st.warning(
                        "Enter your Groq API key before resending."
                    )
                elif new_text.strip():
                    _resend_edited_message(
                        index=index,
                        new_text=new_text.strip(),
                        api_key=api_key,
                    )

        with cancel_column:
            if st.button(
                "✕ Cancel",
                key=f"cancel_{active_chat_id}_{index}",
            ):
                chat_manager.clear_edit_state()
                _rerun()

        return

    message_column, edit_column = st.columns([8, 1])

    with message_column:
        st.markdown(
            f"""
<div class="chat-user">
    <div class="chat-label">🧑 You</div>
    {html_text(entry.get("message", ""))}
</div>
""",
            unsafe_allow_html=True,
        )

    with edit_column:
        st.markdown("<br><br>", unsafe_allow_html=True)

        if st.button(
            "✏️",
            key=f"edit_{active_chat_id}_{index}",
            help="Edit this message",
        ):
            st.session_state.editing_idx = index
            st.session_state.edit_text = entry.get("message", "")
            _rerun()


def _render_bot_message(
    index: int,
    entry: dict[str, Any],
) -> None:
    """Render a bot response, mode badge, sources, and copy control."""
    active_chat_id = chat_manager.get_active_chat_id()

    if entry.get("mode") == "pdf":
        badge = (
            '<span class="mode-badge mode-pdf">'
            "📄 From PDF"
            "</span>"
        )
    else:
        badge = (
            '<span class="mode-badge mode-gen">'
            "✨ General"
            "</span>"
        )

    source_html = ""

    if entry.get("sources"):
        source_items = "<br>".join(
            f"• {html_text(source)}"
            for source in entry["sources"][:3]
        )
        source_html = (
            '<div class="source-box">'
            "<strong>📍 Sources:</strong><br>"
            f"{source_items}"
            "</div>"
        )

    st.markdown(
        f"""
<div class="chat-bot">
    <div class="chat-label">
        🤖 NoteBot &nbsp;{badge}
    </div>
    {html_text(entry.get("message", ""))}
    {source_html}
</div>
""",
        unsafe_allow_html=True,
    )

    _, copy_column = st.columns([6, 1])

    with copy_column:
        copied_key = f"copied_{active_chat_id}_{index}"

        if st.button(
            "📋 Copy",
            key=f"copy_{active_chat_id}_{index}",
        ):
            st.session_state[copied_key] = True

        if st.session_state.get(copied_key):
            st.toast("✅ Copied!", icon="📋")
            st.code(entry.get("message", ""), language=None)


def _resend_edited_message(
    index: int,
    new_text: str,
    api_key: str,
) -> None:
    """Replace an edited message and regenerate the conversation."""
    chat_manager.replace_history_from(index, new_text)

    try:
        with st.spinner("Thinking..."):
            answer, answered_from_pdf, sources = get_answer(
                new_text,
                api_key,
                chat_manager.get_active_chat(),
            )
    except Exception as error:
        answer = (
            "Sorry, I couldn't get a response from Groq. "
            f"{error}"
        )
        answered_from_pdf = False
        sources = []

    chat_manager.add_message(
        {
            "role": "bot",
            "message": answer,
            "mode": (
                "pdf" if answered_from_pdf else "general"
            ),
            "sources": sources,
        }
    )

    chat_manager.clear_edit_state()
    _rerun()

def _queue_new_message(user_query: str) -> None:
    """
    Save the first user message before calling Groq.

    The rerun makes the active conversation appear in the sidebar
    immediately, including while the model is generating its answer.
    """
    active_chat_id = chat_manager.get_active_chat_id()

    chat_manager.add_message(
        {
            "role": "user",
            "message": user_query,
        }
    )

    st.session_state.pending_request = {
        "chat_id": active_chat_id,
        "query": user_query,
    }

    st.rerun()


def _process_pending_request(api_key: str) -> None:
    """Generate a response using the pending chat's isolated state."""
    pending = st.session_state.get("pending_request")

    if not pending:
        return

    chat_id = pending.get("chat_id")
    query = str(pending.get("query", "")).strip()

    if not query or chat_id not in st.session_state.chats:
        st.session_state.pending_request = None
        return

    # Never answer using another chat's history or PDF state.
    if chat_id != chat_manager.get_active_chat_id():
        return

    active_chat = chat_manager.get_active_chat()

    try:
        with st.spinner("Thinking..."):
            answer, from_pdf, sources = get_answer(
                query,
                api_key,
                active_chat,
            )
    except Exception as error:
        answer = (
            "Sorry, I couldn't get a response from Groq. "
            f"{error}"
        )
        from_pdf = False
        sources = []

    chat_manager.add_message(
        {
            "role": "bot",
            "message": answer,
            "mode": "pdf" if from_pdf else "general",
            "sources": sources,
        }
    )

    st.session_state.pending_request = None
    st.rerun()

def _submit_chat_message() -> None:
    """Save the message before Streamlit renders the sidebar."""
    user_query = st.session_state.get("chat_input_box", "")

    if not user_query or not user_query.strip():
        return

    query = user_query.strip()
    active_chat_id = chat_manager.get_active_chat_id()

    chat_manager.add_message(
        {
            "role": "user",
            "message": query,
        }
    )

    st.session_state.pending_request = {
        "chat_id": active_chat_id,
        "query": query,
    }
def render_app() -> None:
    chat_manager.initialize_session()

    theme = _theme()
    apply_styles(theme)

    api_key = render_sidebar(theme)
    render_header(theme)
    render_chat(api_key)

    pending = st.session_state.get("pending_request")

    if pending and api_key.strip():
        _process_pending_request(api_key)
        return

    st.markdown("<br>", unsafe_allow_html=True)

    if not api_key.strip():
        st.warning(
            "👈 Enter your free Groq API key in the sidebar. "
            "Get it at console.groq.com"
        )
        return

    st.chat_input(
        "Ask anything — from PDFs or general knowledge...",
        key="chat_input_box",
        on_submit=_submit_chat_message,
    )