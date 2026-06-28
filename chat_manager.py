"""Independent per-chat session-state management."""

from __future__ import annotations

import copy
import uuid
from typing import Any

import streamlit as st

from utils import current_iso_time, current_time, make_chat_title


def _new_chat() -> dict[str, Any]:
    return {
        "title": "New Chat",
        "time": current_time(),
        "created_at": current_iso_time(),
        "updated_at": current_iso_time(),
        "history": [],
        "pdf_chunks": [],
        "pdf_names": [],
        "memory": [],
    }


def initialize_session() -> None:
    defaults = {
        "dark_mode": True,
        "editing_idx": None,
        "edit_text": "",
        "pending_request": None,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

    if "chats" not in st.session_state:
        chat_id = uuid.uuid4().hex
        st.session_state.chats = {chat_id: _new_chat()}
        st.session_state.chat_order = [chat_id]
        st.session_state.active_chat_id = chat_id

    _repair_state()


def _repair_state() -> None:
    chats = st.session_state.chats

    order = [
        chat_id
        for chat_id in st.session_state.get("chat_order", [])
        if chat_id in chats
    ]

    for chat_id, chat in chats.items():
        if chat_id not in order:
            order.append(chat_id)

        chat.setdefault("history", [])
        chat.setdefault("pdf_chunks", [])
        chat.setdefault("pdf_names", [])
        chat.setdefault(
            "memory",
            copy.deepcopy(chat["history"]),
        )
        chat.setdefault("title", "New Chat")
        chat.setdefault("time", current_time())
        chat.setdefault("created_at", current_iso_time())
        chat.setdefault("updated_at", current_iso_time())

    if not order:
        chat_id = uuid.uuid4().hex
        chats[chat_id] = _new_chat()
        order.append(chat_id)

    st.session_state.chat_order = order

    if st.session_state.get("active_chat_id") not in chats:
        st.session_state.active_chat_id = order[-1]


def get_active_chat_id() -> str:
    return st.session_state.active_chat_id


def get_active_chat() -> dict[str, Any]:
    return st.session_state.chats[get_active_chat_id()]


def list_chats_newest_first() -> list[tuple[str, dict[str, Any]]]:
    return [
        (chat_id, st.session_state.chats[chat_id])
        for chat_id in reversed(st.session_state.chat_order)
    ]


def create_chat() -> str:
    chat_id = uuid.uuid4().hex

    st.session_state.chats[chat_id] = _new_chat()
    st.session_state.chat_order.append(chat_id)
    st.session_state.active_chat_id = chat_id
    st.session_state.pending_request = None

    clear_edit_state()
    return chat_id


def switch_chat(chat_id: str) -> None:
    if chat_id not in st.session_state.chats:
        return

    st.session_state.active_chat_id = chat_id
    clear_edit_state()


def delete_chat(chat_id: str) -> None:
    if chat_id not in st.session_state.chats:
        return

    del st.session_state.chats[chat_id]

    st.session_state.chat_order = [
        existing_id
        for existing_id in st.session_state.chat_order
        if existing_id != chat_id
    ]

    pending = st.session_state.get("pending_request")
    if pending and pending.get("chat_id") == chat_id:
        st.session_state.pending_request = None

    if not st.session_state.chat_order:
        create_chat()
    elif st.session_state.active_chat_id == chat_id:
        st.session_state.active_chat_id = (
            st.session_state.chat_order[-1]
        )

    clear_edit_state()


def add_message(entry: dict[str, Any]) -> None:
    chat = get_active_chat()
    message = copy.deepcopy(entry)

    chat["history"].append(message)
    chat["memory"].append(copy.deepcopy(message))
    _refresh_metadata(chat)


def replace_history_from(index: int, message: str) -> None:
    chat = get_active_chat()

    chat["history"] = chat["history"][:index]
    chat["memory"] = copy.deepcopy(chat["history"])

    add_message(
        {
            "role": "user",
            "message": message,
        }
    )


def set_pdf_state(
    chunks: list[dict[str, str]],
    names: list[str],
) -> None:
    chat = get_active_chat()

    chat["pdf_chunks"] = copy.deepcopy(chunks)
    chat["pdf_names"] = list(names)
    chat["updated_at"] = current_iso_time()


def clear_active_chat() -> None:
    chat = get_active_chat()

    chat["title"] = "New Chat"
    chat["time"] = current_time()
    chat["updated_at"] = current_iso_time()
    chat["history"] = []
    chat["pdf_chunks"] = []
    chat["pdf_names"] = []
    chat["memory"] = []

    st.session_state.pending_request = None
    clear_edit_state()


def reset_all() -> None:
    st.session_state.chats = {}
    st.session_state.chat_order = []
    st.session_state.pending_request = None

    chat_id = uuid.uuid4().hex
    st.session_state.chats[chat_id] = _new_chat()
    st.session_state.chat_order.append(chat_id)
    st.session_state.active_chat_id = chat_id

    clear_edit_state()


def clear_edit_state() -> None:
    st.session_state.editing_idx = None
    st.session_state.edit_text = ""


def _refresh_metadata(chat: dict[str, Any]) -> None:
    first_message = next(
        (
            entry["message"]
            for entry in chat["history"]
            if entry.get("role") == "user"
        ),
        "",
    )

    chat["title"] = make_chat_title(first_message)
    chat["time"] = current_time()
    chat["updated_at"] = current_iso_time()