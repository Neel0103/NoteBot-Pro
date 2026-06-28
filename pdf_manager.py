"""PDF extraction, chunking, and retrieval."""

from __future__ import annotations

from typing import Any, Iterable

from langchain_text_splitters import RecursiveCharacterTextSplitter
from PyPDF2 import PdfReader


def process_pdfs(
    uploaded_files: Iterable[Any],
) -> tuple[list[dict[str, str]], list[str]]:
    """Process uploaded PDFs using the original chunking behavior."""
    all_chunks: list[dict[str, str]] = []
    pdf_names: list[str] = []

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=600,
        chunk_overlap=80,
    )

    for uploaded_file in uploaded_files:
        uploaded_file.seek(0)
        pdf_names.append(uploaded_file.name)
        reader = PdfReader(uploaded_file)

        for page_number, page in enumerate(reader.pages):
            page_text = page.extract_text()

            if page_text:
                for piece in splitter.split_text(page_text):
                    all_chunks.append(
                        {
                            "text": piece,
                            "source": (
                                f"{uploaded_file.name} | "
                                f"Page {page_number + 1}"
                            ),
                        }
                    )

    return all_chunks, pdf_names


def simple_search(
    query: str,
    chunks: list[dict[str, str]],
    top_k: int = 4,
) -> list[dict[str, str]]:
    """Original NoteBot word-overlap retrieval behavior."""
    query_words = set(query.lower().split())
    scored: list[tuple[int, int]] = []

    for index, chunk in enumerate(chunks):
        text_words = set(chunk["text"].lower().split())
        score = len(query_words & text_words)
        scored.append((score, index))

    scored.sort(reverse=True)

    return [
        chunks[index]
        for score, index in scored[:top_k]
        if score > 0
    ]