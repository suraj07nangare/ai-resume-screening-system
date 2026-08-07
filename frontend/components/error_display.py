import streamlit as st

from services.api_client import ApiError


def show_api_error(exc: ApiError) -> None:
    st.error(f"API error ({exc.status_code}): {exc.detail}")
