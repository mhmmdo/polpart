import streamlit as st
from pathlib import Path
from src.config import STYLE_PATH

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

# Create navigation and run the active page
pg = st.navigation([dashboard, data_historis, prediksi, visualisasi, tentang])
pg.run()
