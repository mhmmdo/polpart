import streamlit as st

from src.config import APP_SUBTITLE, APP_TITLE, STYLE_PATH
from src.data_loader import load_dataset, load_uploaded_data


def setup_page(title: str = APP_TITLE):
    # Page config is handled globally in app.py now
    inject_css()


def inject_css():
    if STYLE_PATH.exists():
        st.markdown(f"<style>{STYLE_PATH.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)


def render_header(title: str, subtitle: str | None = None):
    st.markdown(
        f"""
        <div class="hero-container">
            <h1 class="hero-title">{title}</h1>
            <p class="hero-subtitle">{subtitle or ""}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def load_data_from_sidebar():
    st.sidebar.markdown("### Dataset")
    uploaded_file = st.sidebar.file_uploader("Upload CSV data asli", type=["csv"])
    uploaded_data = load_uploaded_data(uploaded_file)
    if uploaded_data is not None:
        st.sidebar.success("Dataset upload dipakai.")
        return uploaded_data

    st.sidebar.info("Memakai data dari database SQLite.")
    return load_dataset()


def sidebar_filters(df):
    years = sorted(df["tahun"].dropna().astype(int).unique().tolist())
    areas = sorted(df["kecamatan"].dropna().unique().tolist())

    selected_years = st.sidebar.multiselect("Filter tahun", years, key="filter_tahun_clean")
    selected_areas = st.sidebar.multiselect("Filter kecamatan", areas, key="filter_kecamatan_clean")
    return selected_years, selected_areas


def metric_card(label: str, value: str, help_text: str | None = None):
    st.metric(label=label, value=value, help=help_text)
