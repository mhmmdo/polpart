import streamlit as st
import pandas as pd

from src.config import FEATURE_COLUMNS
from src.model import predict_participation, train_random_forest
from src.ui import load_data_from_sidebar, render_header, setup_page
from src.utils import format_rupiah
from src.visualizations import feature_importance_bar
from src.database import (
    get_all_kecamatan,
    save_prediction,
    get_prediction_history
)

setup_page("Prediksi")
render_header("Prediksi Random Forest", "Form input variabel sosio-ekonomi untuk memprediksi tingkat partisipasi politik.")

# 1. Mengambil data dari database
df = load_data_from_sidebar()
if df.empty:
    st.warning("Database kosong atau belum diinisialisasi. Silakan jalankan `python scripts/init_db.py` dan `python scripts/import_csv_to_sqlite.py` untuk menginisialisasi database dan mengimpor data awal.")
    st.stop()

try:
    # 2. Model Random Forest otomatis dilatih (belajar) di latar belakang setiap kali halaman ini dibuka
    model_result = train_random_forest(df)
except ValueError as error:
    st.error(str(error))
    st.stop()

# Menampilkan tingkat akurasi (Raport) dari model yang baru saja selesai belajar
col1, col2, col3 = st.columns(3)
col1.metric("RMSE", f"{model_result.rmse:.3f}")
col2.metric("R²", f"{model_result.r2:.3f}")
col3.metric("Jumlah Data", len(df))

st.markdown("---")
st.markdown("### Form Input Variabel")

# Mengambil daftar nama-nama kecamatan dari database untuk dimasukkan ke pilihan dropdown (ComboBox)
try:
    kec_df = get_all_kecamatan()
    kec_options = ["-- Tanpa Kecamatan --"] + list(kec_df["nama_kecamatan"].unique())
except Exception:
    kec_options = ["-- Tanpa Kecamatan --"]

# Membuat formulir agar pengguna bisa memasukkan angka (fitur/soal) untuk ditebak oleh mesin
with st.form("prediction_form"):
    left, right = st.columns(2)
    with left:
        kecamatan_val = st.selectbox("Kecamatan (opsional)", options=kec_options)
        tahun_val = st.number_input("Tahun prediksi (opsional)", min_value=2000, max_value=2100, value=2025)
        tingkat_pendidikan = st.slider("Tingkat pendidikan (%)", 0.0, 100.0, 73.0, 0.1)
        pendapatan_per_kapita = st.number_input("Pendapatan per kapita (Rp)", min_value=0, value=32000000, step=500000)
    with right:
        tingkat_pengangguran = st.slider("Tingkat pengangguran (%)", 0.0, 20.0, 5.0, 0.1)
        kepadatan_penduduk = st.number_input("Kepadatan penduduk", min_value=0, value=8500, step=100)
        ipm = st.slider("IPM", 0.0, 100.0, 77.0, 0.1)

    # Tombol submit ditekan
    submit = st.form_submit_button("Prediksi")

# Menyimpan nilai yang dimasukkan dari form ke dalam objek kamus (dictionary) Python
input_values = {
    "tingkat_pendidikan": tingkat_pendidikan,
    "pendapatan_per_kapita": pendapatan_per_kapita,
    "tingkat_pengangguran": tingkat_pengangguran,
    "kepadatan_penduduk": kepadatan_penduduk,
    "ipm": ipm,
}

# Jika tombol "Prediksi" diklik
if submit:
    # Memanggil fungsi tebakan model dengan memberikan soal (input_values)
    prediction = predict_participation(model_result.model, input_values)
    
    # Mengatur jika kecamatan tidak dipilih maka set menjadi None
    kec_to_save = None if kecamatan_val == "-- Tanpa Kecamatan --" else kecamatan_val
    
    # Menyimpan hasil tebakan ke dalam database (tabel riwayat)
    try:
        save_prediction({
            "kecamatan": kec_to_save,
            "tahun": int(tahun_val),
            "tingkat_pendidikan": tingkat_pendidikan,
            "pendapatan_per_kapita": pendapatan_per_kapita,
            "tingkat_pengangguran": tingkat_pengangguran,
            "kepadatan_penduduk": kepadatan_penduduk,
            "ipm": ipm,
            "hasil_prediksi": prediction
        })
        st.success("Hasil prediksi berhasil disimpan ke database!")
    except Exception as e:
        st.warning(f"Gagal menyimpan riwayat prediksi ke database: {e}")

    # Menampilkan angka hasil prediksi dengan kotak desain HTML Custom 
    st.markdown(
        f"""
        <div class="prediction-card">
            <div class="prediction-title">Hasil Prediksi Random Forest</div>
            <div style="font-size: 2.5rem; font-weight: 800; color: #2563EB; margin: 0.5rem 0; line-height: 1;">
                {prediction:.2f}%
            </div>
            <p style="margin: 0; font-size: 0.95rem; opacity: 0.85;">
                Estimasi tingkat partisipasi politik berdasarkan nilai variabel sosio-ekonomi yang dimasukkan.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Menampilkan ulang angka yang baru saja diketik pengguna
    st.markdown("#### Detail Input")
    col_a, col_b, col_c = st.columns(3)
    col_a.markdown(f"**Kecamatan**: {kecamatan_val}")
    col_a.markdown(f"**Tahun**: {tahun_val}")
    col_b.markdown(f"**Pendidikan**: {tingkat_pendidikan:.1f}%")
    col_b.markdown(f"**Pendapatan**: {format_rupiah(pendapatan_per_kapita)}")
    col_c.markdown(f"**Pengangguran**: {tingkat_pengangguran:.1f}%")
    col_c.markdown(f"**Kepadatan Penduduk**: {kepadatan_penduduk:,.0f}".replace(",", "."))
    col_c.markdown(f"**IPM**: {ipm:.1f}")

st.markdown("---")
# Menampilkan grafik yang memberitahu faktor mana yang paling mempengaruhi partisipasi (cth: IPM/Pendidikan)
st.plotly_chart(feature_importance_bar(model_result.feature_importance), width="stretch")
st.caption("Feature importance menunjukkan kontribusi relatif dari masing-masing variabel terhadap prediksi model Random Forest. Nilai ini didasarkan pada signifikansi statistik dalam model.")

# Bagian Tabel Riwayat Prediksi
st.markdown("---")
st.markdown("### Riwayat Prediksi")
try:
    # Membaca seluruh histori dari database
    history_df = get_prediction_history()
    if history_df.empty:
        st.info("Belum ada riwayat prediksi.")
    else:
        # Mengganti nama kolom bahasa database menjadi bahasa manusia (agar rapi di tabel)
        display_history = history_df.rename(columns={
            "id_prediksi": "ID",
            "kecamatan": "Kecamatan",
            "tahun": "Tahun",
            "tingkat_pendidikan": "Pendidikan (%)",
            "pendapatan_per_kapita": "Pendapatan per Kapita",
            "tingkat_pengangguran": "Pengangguran (%)",
            "kepadatan_penduduk": "Kepadatan",
            "ipm": "IPM",
            "hasil_prediksi": "Hasil Prediksi (%)",
            "created_at": "Waktu Prediksi"
        })
        # Merapikan format tampilan uang Rupiah dan persentase
        display_history["Pendapatan per Kapita"] = display_history["Pendapatan per Kapita"].apply(format_rupiah)
        display_history["Hasil Prediksi (%)"] = display_history["Hasil Prediksi (%)"].apply(lambda x: f"{x:.2f}%")
        
        # Menampilkan tabelnya di web
        st.dataframe(display_history, width="stretch", hide_index=True)
except Exception as e:
    st.error(f"Gagal memuat riwayat prediksi: {e}")
