"""NoteBot Pro application entry point."""

import streamlit as st

from ui import render_app


st.set_page_config(
    page_title="NoteBot Pro",
    page_icon="🤖",
    layout="wide",
)

render_app()