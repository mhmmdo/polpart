import streamlit as st
from pathlib import Path
from src.config import STYLE_PATH
from streamlit_option_menu import option_menu

# Set page config globally (Only once in the main entry point!)
st.set_page_config(
    page_title="Sistem Prediksi Partisipasi Politik",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Inject custom styling globally
if STYLE_PATH.exists():
    st.markdown(f"<style>{STYLE_PATH.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)

# Define pages for multi-page navigation
dashboard = st.Page("pages/1_Dashboard.py", title="Dashboard", default=True)
data_historis = st.Page("pages/2_Data_Historis.py", title="Data Historis")
prediksi = st.Page("pages/3_Prediksi.py", title="Prediksi RF")
visualisasi = st.Page("pages/4_Visualisasi.py", title="Visualisasi & Peta")
tentang = st.Page("pages/5_Tentang.py", title="Tentang Aplikasi")

# Custom navigation menu with streamlit-option-menu
page_names = ["Dashboard", "Data Historis", "Prediksi", "Visualisasi", "Tentang"]
page_files = [
    "pages/1_Dashboard.py",
    "pages/2_Data_Historis.py",
    "pages/3_Prediksi.py",
    "pages/4_Visualisasi.py",
    "pages/5_Tentang.py"
]

current_page = st.session_state.get("current_page", "Dashboard")
try:
    default_index = page_names.index(current_page)
except ValueError:
    default_index = 0

with st.sidebar:
    selected = option_menu(
        "PolPart RF",
        options=page_names,
        icons=["grid-fill", "table", "cpu", "map-fill", "info-circle-fill"],
        menu_icon="activity",
        default_index=default_index,
        styles={
            "container": {"background-color": "#ffffff", "padding": "5px 0px"},
            "icon": {"color": "#475569", "font-size": "15px"},
            "menu-title": {"color": "#1E293B", "font-family": "Plus Jakarta Sans", "font-weight": "800"},
            "nav-link": {
                "color": "#475569",
                "font-family": "Plus Jakarta Sans",
                "font-weight": "600",
                "font-size": "13px",
                "text-align": "left",
                "margin": "0px",
            },
            "nav-link-selected": {"background-color": "#ff7f66", "color": "#FFFFFF"},
        }
    )

if selected != current_page:
    st.session_state["current_page"] = selected
    st.switch_page(page_files[page_names.index(selected)])

# Create navigation and run the active page
pg = st.navigation([dashboard, data_historis, prediksi, visualisasi, tentang])
pg.run()
