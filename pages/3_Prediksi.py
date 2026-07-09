import streamlit as st
import pandas as pd

from src.config import FEATURE_COLUMNS
from src.model import predict_participation, train_random_forest
from src.ui import load_data_from_sidebar, render_header, setup_page
from src.database import (
    get_all_kecamatan,
    save_prediction,
    get_prediction_history,
    get_connection
)
from src.pdf_generator import generate_recap_pdf

setup_page("Prediksi")
render_header("Prediksi Random Forest", "Simulasi prediksi tingkat partisipasi politik TPS menggunakan parameter demografi demografis.")

# 1. Mengambil data dari database
df = load_data_from_sidebar()
if df.empty:
    st.warning("Database kosong atau belum diinisialisasi. Hubungi Admin untuk mengunggah CSV data awal.")
    st.stop()

try:
    # 2. Latih model Random Forest otomatis
    model_result = train_random_forest(df)
except ValueError as error:
    st.error(str(error))
    st.stop()

# Menampilkan metrik model
col1, col2, col3 = st.columns(3)
col1.metric("RMSE Model", f"{model_result.rmse:.4f}")
col2.metric("R² Score", f"{model_result.r2:.4f} ({model_result.r2*100:.1f}%)")
col3.metric("Total Sampel TPS", len(df))

st.markdown("---")
st.markdown("### Form Input Simulasi Prediksi")

try:
    kec_df = get_all_kecamatan()
    kec_options = ["-- Tanpa Kecamatan --"] + list(kec_df["nama_kecamatan"].unique())
except Exception:
    kec_options = ["-- Tanpa Kecamatan --"]

# Form input parameter
with st.form("prediction_form"):
    left, right = st.columns(2)
    with left:
        kecamatan_val = st.selectbox("Kecamatan", options=kec_options)
        kelurahan_val = st.text_input("Nama Kelurahan / Desa", value="BASIRIH")
        no_tps_val = st.text_input("Nomor TPS", value="001")
        dpt_val = st.number_input("Jumlah Daftar Pemilih Tetap (DPT) TPS", min_value=1, value=250, step=10)
    with right:
        rasio_dpt = st.slider("Rasio DPT Terhadap Penduduk Kelurahan", 0.0, 3.0, 1.20, 0.01)
        usia_17_24 = st.slider("Pemilih Usia 17 - 24 Tahun (%)", 0.0, 100.0, 13.6, 0.1)
        usia_25_44 = st.slider("Pemilih Usia 25 - 44 Tahun (%)", 0.0, 100.0, 29.7, 0.1)
        usia_45_plus = st.slider("Pemilih Usia 45 Tahun Keatas (%)", 0.0, 100.0, 32.2, 0.1)

    submit = st.form_submit_button("Lakukan Prediksi")

if submit:
    input_values = {
        "dpt": dpt_val,
        "rasio_dpt_terhadap_penduduk_kelurahan": rasio_dpt,
        "persen_usia_17_24_kec": usia_17_24,
        "persen_usia_25_44_kec": usia_25_44,
        "persen_usia_45_plus_kec": usia_45_plus,
    }
    
    # Hitung prediksi
    prediction = predict_participation(model_result.model, input_values)
    kec_to_save = None if kecamatan_val == "-- Tanpa Kecamatan --" else kecamatan_val
    
    # Simpan riwayat
    try:
        save_prediction({
            "kecamatan": kec_to_save,
            "kelurahan": kelurahan_val.strip().upper(),
            "no_tps": no_tps_val.strip(),
            "dpt": dpt_val,
            "rasio_dpt": rasio_dpt,
            "usia_17_24": usia_17_24,
            "usia_25_44": usia_25_44,
            "usia_45_plus": usia_45_plus,
            "hasil_prediksi": prediction
        })
        st.success("Hasil prediksi berhasil disimpan ke database!")
    except Exception as e:
        st.warning(f"Gagal menyimpan riwayat ke database: {e}")

    # Card hasil prediksi
    st.markdown(
        f"""
        <div class="prediction-card" style="background-color: #ffffff; padding: 25px; border-radius: 12px; box-shadow: 0 4px 10px rgba(0,0,0,0.05); border-left: 6px solid #ff7f66; margin: 15px 0;">
            <div class="prediction-title" style="font-weight: 800; font-size: 1rem; color: #64748b; text-transform: uppercase; margin-bottom: 5px;">Hasil Prediksi Partisipasi Politik</div>
            <div style="font-size: 2.8rem; font-weight: 800; color: #ff7f66; line-height: 1.2;">
                {prediction:.2f}%
            </div>
            <p style="margin: 5px 0 0 0; font-size: 0.95rem; color: #334155;">
                Estimasi keikutsertaan pemilih di TPS {no_tps_val} Kelurahan {kelurahan_val.upper()} (Kecamatan {kecamatan_val})
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    # Sediakan file PDF untuk didownload
    try:
        pdf_data = {
            "kecamatan": kecamatan_val,
            "kelurahan": kelurahan_val.strip().upper(),
            "no_tps": no_tps_val.strip(),
            "dpt": dpt_val,
            "rasio_dpt": rasio_dpt,
            "usia_17_24": usia_17_24,
            "usia_25_44": usia_25_44,
            "usia_45_plus": usia_45_plus,
            "hasil_prediksi": prediction,
            "model_metrics": {
                "rmse": model_result.rmse,
                "r2": model_result.r2
            },
            "printed_by": st.session_state.get("username", "Guest")
        }
        pdf_bytes = generate_recap_pdf(pdf_data)
        
        st.download_button(
            label="Unduh Rekap PDF Laporan",
            data=pdf_bytes,
            file_name=f"rekap_prediksi_{kelurahan_val.strip().replace(' ', '_')}_tps{no_tps_val}.pdf",
            mime="application/pdf",
            use_container_width=True
        )
    except Exception as pdf_err:
        st.error(f"Gagal menyiapkan file PDF unduhan: {pdf_err}")

    # Detail Input
    st.markdown("#### Detail Parameter Input")
    col_a, col_b, col_c = st.columns(3)
    col_a.markdown(f"**Kecamatan**: {kecamatan_val}")
    col_a.markdown(f"**Kelurahan**: {kelurahan_val}")
    col_a.markdown(f"**Nomor TPS**: {no_tps_val}")
    col_b.markdown(f"**Jumlah DPT**: {dpt_val:,}".replace(",", "."))
    col_b.markdown(f"**Rasio DPT**: {rasio_dpt:.4f}")
    col_c.markdown(f"**Usia 17-24 (%)**: {usia_17_24:.1f}%")
    col_c.markdown(f"**Usia 25-44 (%)**: {usia_25_44:.1f}%")
    col_c.markdown(f"**Usia 45+ (%)**: {usia_45_plus:.1f}%")

st.markdown("---")
from src.visualizations import feature_importance_bar
st.plotly_chart(feature_importance_bar(model_result.feature_importance), use_container_width=True, theme=None)
st.caption("Feature importance menunjukkan kontribusi relatif dari masing-masing variabel demografi terhadap prediksi model Random Forest.")

# Tabel Riwayat Prediksi
st.markdown("---")
st.markdown("### Riwayat Prediksi")
try:
    history_df = get_prediction_history()
    if history_df.empty:
        st.info("Belum ada riwayat prediksi.")
    else:
        display_history = history_df.rename(columns={
            "id_prediksi": "ID",
            "kecamatan": "Kecamatan",
            "kelurahan": "Kelurahan",
            "no_tps": "No TPS",
            "dpt": "DPT",
            "rasio_dpt": "Rasio DPT",
            "usia_17_24": "Usia 17-24 (%)",
            "usia_25_44": "Usia 25-44 (%)",
            "usia_45_plus": "Usia 45+ (%)",
            "hasil_prediksi": "Hasil Prediksi (%)",
            "created_at": "Tanggal Analisa"
        })
        # Format persentase hasil prediksi
        display_history["Hasil Prediksi (%)"] = display_history["Hasil Prediksi (%)"].apply(lambda x: f"{x:.2f}%")
        st.dataframe(display_history, use_container_width=True, hide_index=True)
except Exception as e:
    st.error(f"Gagal memuat riwayat prediksi: {e}")
