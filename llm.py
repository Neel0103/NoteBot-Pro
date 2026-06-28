"""Groq-backed PDF and general-chat response generation."""

from __future__ import annotations

from typing import Any

from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

from pdf_manager import simple_search


MODEL_NAME = "meta-llama/llama-4-scout-17b-16e-instruct"


def get_answer(
    user_query: str,
    api_key: str,
    chat: dict[str, Any],
) -> tuple[str, bool, list[str]]:
    llm = ChatGroq(
        api_key=api_key,
        model=MODEL_NAME,
        temperature=0,
        max_tokens=600,
    )

    history_text = ""

    for entry in chat["history"]:
        if entry["role"] == "user":
            history_text += f"User: {entry['message']}\n"
        else:
            history_text += f"Assistant: {entry['message']}\n"

    pdf_chunks = chat.get("pdf_chunks", [])

    if pdf_chunks:
        normalized_query = (
            user_query.lower()
            .replace("!", "")
            .replace("?", "")
            .replace(".", "")
            .replace(",", "")
        )
        query_words = set(normalized_query.split())

        pdf_reference_words = {
            "pdf",
            "document",
            "file",
            "uploaded",
            "upload",
        }

        is_direct_pdf_request = bool(
            query_words.intersection(pdf_reference_words)
        )

        if is_direct_pdf_request:
            # For summaries or general PDF questions, lexical search
            # produces irrelevant matches such as "this" and "about".
            # Use representative context from the document directly.
            matches = pdf_chunks[:8]
        else:
            matches = simple_search(
                user_query,
                pdf_chunks,
                top_k=4,
            )

        if matches:
            context = "\n\n".join(
                match["text"] for match in matches
            )
            sources = list(
                dict.fromkeys(
                    match["source"] for match in matches
                )
            )

            pdf_prompt = ChatPromptTemplate.from_template(
                """
You are a helpful tutor answering questions about an uploaded PDF.

Use only the supplied PDF context.

If the user asks what the PDF or document is about, provide a useful
summary of the supplied context. Do not reply NOT_IN_PDF for a general
summary or overview request.

For a specific factual question, if the answer genuinely does not
appear in the context, reply exactly: NOT_IN_PDF

Conversation so far:
{history}

PDF context:
{context}

Question: {input}
"""
            )

            pdf_answer = (pdf_prompt | llm).invoke(
                {
                    "input": user_query,
                    "context": context,
                    "history": history_text,
                }
            ).content.strip()

            if is_direct_pdf_request:
                return pdf_answer, True, sources

            if "NOT_IN_PDF" not in pdf_answer:
                return pdf_answer, True, sources

    general_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are NoteBot Pro, a smart helpful AI. "
                "Answer clearly and concisely.",
            ),
            (
                "human",
                "History:\n{history}\n\nQuestion: {input}",
            ),
        ]
    )

    general_answer = (general_prompt | llm).invoke(
        {
            "history": history_text,
            "input": user_query,
        }
    ).content.strip()

    return general_answer, False, []