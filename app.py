"""Aria AI Pro — Streamlit entry point."""

import streamlit as st

from aria.ui.main import render_app

st.set_page_config(
    page_title="Aria AI Pro",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded",
)
render_app()
