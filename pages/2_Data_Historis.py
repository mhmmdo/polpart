import streamlit as st
import pandas as pd

from src.config import DISPLAY_NAMES, TARGET_COLUMN
from src.data_loader import filter_dataset
from src.model import train_random_forest
from src.ui import load_data_from_sidebar, render_header, setup_page, sidebar_filters
from src.utils import rename_for_display
from src.visualizations import feature_importance_bar, prediction_scatter
from src.database import (
    get_all_kecamatan,
    insert_or_update_sosio_ekonomi,
    insert_or_update_partisipasi
)

setup_page("Data Historis")
render_header("Data Historis", "Tabel data sosio-ekonomi dan partisipasi politik dari SQLite database, filter, serta evaluasi Random Forest.")

# Load database source indicator
st.info("Sumber penyimpanan utama: **SQLite Database (database/polpart.db)**")

df = load_data_from_sidebar()

if df.empty:
    st.warning("Database kosong atau belum diinisialisasi. Anda dapat mengimpor data awal dari CSV template, atau menambahkan data secara manual melalui form di bawah.")
else:
    selected_years, selected_areas = sidebar_filters(df)
    filtered_df = filter_dataset(df, selected_years, selected_areas)

    if filtered_df.empty:
        st.warning("Data kosong setelah filter.")
    else:
        keyword = st.text_input("Cari kecamatan", placeholder="Contoh: Banjarmasin Timur")
        if keyword:
            filtered_df = filtered_df[filtered_df["kecamatan"].str.contains(keyword, case=False, na=False)]

        st.markdown("### Tabel Data")
        st.dataframe(rename_for_display(filtered_df), use_container_width=True, hide_index=True)

        csv = filtered_df.to_csv(index=False).encode("utf-8")
        st.download_button("Download data hasil filter", data=csv, file_name="data_hasil_filter.csv", mime="text/csv")

        st.markdown("---")
        st.markdown("### Evaluasi Model Random Forest")
        try:
            model_result = train_random_forest(filtered_df)
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("RMSE", f"{model_result.rmse:.3f}")
            col2.metric("R²", f"{model_result.r2:.3f}")
            col3.metric("Data Training", model_result.train_size)
            col4.metric("Data Testing", model_result.test_size)

            left, right = st.columns(2)
            with left:
                st.plotly_chart(feature_importance_bar(model_result.feature_importance), use_container_width=True)
            with right:
                st.plotly_chart(prediction_scatter(model_result.prediction_result), use_container_width=True)

            st.markdown("#### Hasil Aktual vs Prediksi")
            st.dataframe(model_result.prediction_result, use_container_width=True, hide_index=True)
        except ValueError as error:
            st.warning(str(error))

st.markdown("---")
st.markdown("### Manajemen Input Data (Manual)")

# Load kecamatan list for dropdown
try:
    kec_df = get_all_kecamatan()
    kec_list = list(kec_df["nama_kecamatan"].unique())
except Exception:
    kec_list = []

col_form1, col_form2 = st.columns(2)

with col_form1:
    with st.expander("Tambah / Update Data Sosio-Ekonomi"):
        with st.form("form_sosio"):
            # Kecamatan selection
            selected_kec = st.selectbox(
                "Pilih Kecamatan", 
                options=kec_list + ["-- Tambah Kecamatan Baru --"],
                key="sosio_kec"
            )
            new_kec_name = st.text_input("Nama Kecamatan Baru (jika opsi di atas dipilih)", key="sosio_new_kec")
            
            tahun = st.number_input("Tahun", min_value=2000, max_value=2100, value=2025, key="sosio_tahun")
            tingkat_pendidikan = st.slider("Tingkat Pendidikan (%)", 0.0, 100.0, 75.0, 0.1, key="sosio_pend")
            pendapatan_per_kapita = st.number_input("Pendapatan per Kapita (Rp)", min_value=0, value=30000000, step=500000, key="sosio_pendapatan")
            tingkat_pengangguran = st.slider("Tingkat Pengangguran (%)", 0.0, 50.0, 5.0, 0.1, key="sosio_peng")
            kepadatan_penduduk = st.number_input("Kepadatan Penduduk", min_value=0, value=5000, step=100, key="sosio_kepadatan")
            ipm = st.slider("IPM", 0.0, 100.0, 75.0, 0.1, key="sosio_ipm")
            
            submit_sosio = st.form_submit_button("Simpan Data Sosio-Ekonomi")
            
            if submit_sosio:
                kecamatan_to_save = new_kec_name.strip() if selected_kec == "-- Tambah Kecamatan Baru --" else selected_kec
                if not kecamatan_to_save or kecamatan_to_save == "-- Tambah Kecamatan Baru --":
                    st.error("Nama kecamatan tidak boleh kosong.")
                else:
                    try:
                        insert_or_update_sosio_ekonomi({
                            "kecamatan": kecamatan_to_save,
                            "tahun": int(tahun),
                            "tingkat_pendidikan": tingkat_pendidikan,
                            "pendapatan_per_kapita": pendapatan_per_kapita,
                            "tingkat_pengangguran": tingkat_pengangguran,
                            "kepadatan_penduduk": kepadatan_penduduk,
                            "ipm": ipm
                        })
                        st.success(f"Data sosio-ekonomi {kecamatan_to_save} tahun {tahun} berhasil disimpan!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Gagal menyimpan data: {e}")

with col_form2:
    with st.expander("Tambah / Update Data Partisipasi Politik"):
        with st.form("form_partisipasi"):
            selected_kec_p = st.selectbox(
                "Pilih Kecamatan", 
                options=kec_list + ["-- Tambah Kecamatan Baru --"],
                key="part_kec"
            )
            new_kec_name_p = st.text_input("Nama Kecamatan Baru (jika opsi di atas dipilih)", key="part_new_kec")
            
            tahun_p = st.number_input("Tahun", min_value=2000, max_value=2100, value=2025, key="part_tahun")
            dpt = st.number_input("Jumlah DPT", min_value=0, value=100000, step=1000, key="part_dpt")
            pengguna_hak_pilih = st.number_input("Pengguna Hak Pilih", min_value=0, value=75000, step=1000, key="part_pemilih")
            sumber_data = st.text_input("Sumber Data", value="KPU Kota Banjarmasin", key="part_sumber")
            
            submit_part = st.form_submit_button("Simpan Data Partisipasi")
            
            if submit_part:
                kecamatan_to_save = new_kec_name_p.strip() if selected_kec_p == "-- Tambah Kecamatan Baru --" else selected_kec_p
                if not kecamatan_to_save or kecamatan_to_save == "-- Tambah Kecamatan Baru --":
                    st.error("Nama kecamatan tidak boleh kosong.")
                elif dpt <= 0:
                    st.error("Jumlah DPT harus lebih dari 0.")
                elif pengguna_hak_pilih > dpt:
                    st.error("Pengguna hak pilih tidak boleh melebihi jumlah DPT.")
                else:
                    try:
                        # partisipasi_politik will be auto-calculated in insert_or_update_partisipasi
                        insert_or_update_partisipasi({
                            "kecamatan": kecamatan_to_save,
                            "tahun": int(tahun_p),
                            "dpt": int(dpt),
                            "pengguna_hak_pilih": int(pengguna_hak_pilih),
                            "sumber_data": sumber_data
                        })
                        st.success(f"Data partisipasi {kecamatan_to_save} tahun {tahun_p} berhasil disimpan!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Gagal menyimpan data: {e}")
