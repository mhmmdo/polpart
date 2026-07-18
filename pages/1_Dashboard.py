import streamlit as st
from src.ui import render_header, setup_page

setup_page("Dashboard")

# Header Utama PolPart RF (Tanpa Emoticon)
render_header("PolPart RF", "Sistem Analisis Prediktif Tingkat Partisipasi Politik Kota Banjarmasin")

# Grid Tombol Pintas Fitur Prediksi & Analisis (Tanpa Emoticon)
st.markdown("### Fitur Utama Sistem Prediksi dan Analisis")
col_sh1, col_sh2 = st.columns(2)

with col_sh1:
    st.markdown(
        """
        <div style="background-color: #ffffff; padding: 20px; border-radius: 8px; border: 1px solid #e2e8f0; border-left: 4px solid #ff7f66; margin-bottom: 15px;">
            <h4 style="margin: 0; font-size: 1.1rem; color: #1e293b;">Analisis Prediktif</h4>
            <p style="margin: 5px 0 15px 0; font-size: 0.85rem; color: #64748b;">Jalankan simulasi prediksi tingkat kehadiran pemilih di lokasi TPS Kota Banjarmasin berbasis parameter demografi.</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.page_link("pages/3_Prediksi.py", label="Buka Halaman Prediksi dan Simulasi", use_container_width=True)
    
    st.markdown(
        """
        <div style="background-color: #ffffff; padding: 20px; border-radius: 8px; border: 1px solid #e2e8f0; border-left: 4px solid #ff7f66; margin-top: 25px; margin-bottom: 15px;">
            <h4 style="margin: 0; font-size: 1.1rem; color: #1e293b;">Visualisasi Spasial dan Korelasi</h4>
            <p style="margin: 5px 0 15px 0; font-size: 0.85rem; color: #64748b;">Pantau peta interaktif sebaran partisipasi politik per kecamatan serta diagram hubungan variabel sosial ekonomi.</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.page_link("pages/4_Visualisasi.py", label="Buka Peta Spasial dan Grafik Korelasi", use_container_width=True)

with col_sh2:
    st.markdown(
        """
        <div style="background-color: #ffffff; padding: 20px; border-radius: 8px; border: 1px solid #e2e8f0; border-left: 4px solid #ff7f66; margin-bottom: 15px;">
            <h4 style="margin: 0; font-size: 1.1rem; color: #1e293b;">Data Historis TPS</h4>
            <p style="margin: 5px 0 15px 0; font-size: 0.85rem; color: #64748b;">Lihat detail rekapitulasi data DPT, jumlah kehadiran pemilih, dan persentase partisipasi TPS dari pemilu sebelumnya.</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.page_link("pages/2_Data_Historis.py", label="Lihat Tabel Data TPS", use_container_width=True)
    
    st.markdown(
        """
        <div style="background-color: #ffffff; padding: 20px; border-radius: 8px; border: 1px solid #e2e8f0; border-left: 4px solid #ff7f66; margin-top: 25px; margin-bottom: 15px;">
            <h4 style="margin: 0; font-size: 1.1rem; color: #1e293b;">Kinerja Evaluasi Model</h4>
            <p style="margin: 5px 0 15px 0; font-size: 0.85rem; color: #64748b;">Pantau keandalan model regresi Random Forest melalui nilai error (RMSE, MAE, R² Score) dan variabel paling berpengaruh.</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.page_link("pages/3_Prediksi.py", label="Buka Hasil Evaluasi Model", use_container_width=True)
