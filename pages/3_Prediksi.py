import streamlit as st
import pandas as pd

from src.config import FEATURE_COLUMNS
import importlib
import src.model
importlib.reload(src.model)
from src.model import predict_participation, train_random_forest
from src.ui import load_data_from_sidebar, render_header, setup_page
from src.database import (
    get_all_kecamatan,
    save_prediction,
    get_prediction_history,
    get_kelurahannya_by_kecamatan,
    get_tps_by_kelurahan,
    get_tps_demographics
)
from src.pdf_generator import generate_recap_pdf
from src.visualizations import feature_importance_bar, prediction_scatter

setup_page("Prediksi")
render_header("Prediksi Random Forest", "Simulasi prediksi tingkat partisipasi politik TPS menggunakan parameter demografi aktual.")

# 1. Mengambil data dari database
df = load_data_from_sidebar()
if df.empty:
    st.warning("Database kosong atau belum diinisialisasi. Hubungi Admin untuk mengunggah CSV data awal.")
    st.stop()

# 2. Pilihan Tahun Pemilu Aktif di atas halaman secara global (Page-level selectbox)
years = sorted(df["tahun"].dropna().astype(int).unique().tolist())
default_index = years.index(2024) if 2024 in years else len(years) - 1
active_year = st.selectbox("Pilih Tahun Pemilu Aktif", years, index=default_index, key="prediksi_global_tahun")

# 3. Saring data khusus tahun aktif untuk pelatihan model secara fleksibel
df_train = df[df["tahun"] == active_year]

try:
    # 4. Latih model Random Forest otomatis berdasarkan data tahun aktif
    model_result = train_random_forest(df_train)
except ValueError as error:
    st.error(f"Gagal melatih model untuk tahun {active_year}: {error}")
    st.stop()

# Membuat tiga tab halaman Prediksi
tab_dashboard, tab_prediksi, tab_evaluasi = st.tabs(["Dashboard Analitik", "Simulasi Prediksi TPS", "Evaluasi Kinerja Model"])

# ------------------ TAB 1: DASHBOARD ANALITIK ------------------
with tab_dashboard:
    st.markdown(f"### Ringkasan Data Partisipasi Politik Pemilu {active_year}")
    
    # Filter Kecamatan di halaman utama (page-level multiselect)
    areas = sorted(df["kecamatan"].dropna().unique().tolist())
    selected_areas = st.multiselect("Saring Berdasarkan Kecamatan", areas, key="prediksi_db_kec_filter")
    
    # Terapkan penyaringan untuk tab dashboard
    filtered_df = df[df["tahun"] == active_year]
    if selected_areas:
        filtered_df = filtered_df[filtered_df["kecamatan"].isin(selected_areas)]
    
    if filtered_df.empty:
        st.warning("Data kosong setelah filter.")
    else:
        has_partisipasi = filtered_df["partisipasi_politik"].notna().any()
        if not has_partisipasi:
            st.warning("Data partisipasi politik belum tersedia.")
        else:
            from src.data_loader import get_summary_2024
            from src.ui import custom_metric_card
            from src.utils import format_percent
            
            summary_active = get_summary_2024(filtered_df)
            
            col_db1, col_db2, col_db3, col_db4 = st.columns(4)
            with col_db1:
                st.html(custom_metric_card("TOTAL TPS", f"{summary_active['total_tps']:,}".replace(",", "."), "", f"TPS Terdaftar ({active_year})", "neutral"))
            with col_db2:
                st.html(custom_metric_card("TOTAL DPT", f"{summary_active['total_dpt']:,}".replace(",", "."), "", "Daftar Pemilih Tetap", "neutral"))
            with col_db3:
                st.html(custom_metric_card("PENGGUNA HAK PILIH", f"{summary_active['total_pengguna']:,}".replace(",", "."), "", "Jumlah Pemilih Hadir", "neutral"))
            with col_db4:
                st.html(custom_metric_card("RATA-RATA PARTISIPASI", format_percent(summary_active["average_partisipasi"]), "", "Rata-rata Kehadiran", "up"))
                
            st.markdown("<br>", unsafe_allow_html=True)
            col_t1, col_t2 = st.columns(2)
            with col_t1:
                st.html(custom_metric_card("PARTISIPASI TERTINGGI (TPS)", f"{summary_active['highest_value']:.2f}%", "", summary_active['highest_area'], "up"))
            with col_t2:
                st.html(custom_metric_card("PARTISIPASI TERENDAH (TPS)", f"{summary_active['lowest_value']:.2f}%", "", summary_active['lowest_area'], "down"))
                
            st.markdown("---")
            
            chart_df = filtered_df.dropna(subset=["partisipasi_politik"])
            
            col_left, col_right = st.columns(2)
            with col_left:
                from src.visualizations import participation_by_area
                st.plotly_chart(participation_by_area(chart_df), use_container_width=True, theme=None)
            with col_right:
                from src.visualizations import dynamic_participation_comparison_chart
                
                # Pilihan tahun pemilu untuk dibandingkan secara lokal
                st.markdown("##### Bandingkan Tahun Pemilu")
                col_y1, col_y2 = st.columns(2)
                all_years = sorted(df["tahun"].dropna().astype(int).unique().tolist())
                with col_y1:
                    comp_year1 = st.selectbox("Tahun 1", all_years, index=0, key="comp_y1")
                with col_y2:
                    idx_default_y2 = all_years.index(2024) if 2024 in all_years else len(all_years) - 1
                    comp_year2 = st.selectbox("Tahun 2", all_years, index=idx_default_y2, key="comp_y2")
                
                # Hitung data perbandingan secara dinamis dari database
                if comp_year1 == comp_year2:
                    st.warning("Silakan pilih dua tahun pemilu yang berbeda untuk melihat perbandingan.")
                else:
                    from src.database import get_connection
                    try:
                        with get_connection() as conn:
                            df_y1 = pd.read_sql_query("""
                                SELECT kecamatan, SUM(dpt) as dpt, SUM(pengguna_hak_pilih) as pengguna
                                FROM data_partisipasi_tps
                                WHERE tahun_pemilu = ?
                                GROUP BY kecamatan
                            """, conn, params=(int(comp_year1),))
                            df_y2 = pd.read_sql_query("""
                                SELECT kecamatan, SUM(dpt) as dpt, SUM(pengguna_hak_pilih) as pengguna
                                FROM data_partisipasi_tps
                                WHERE tahun_pemilu = ?
                                GROUP BY kecamatan
                            """, conn, params=(int(comp_year2),))
                            
                        if not df_y1.empty and not df_y2.empty:
                            df_y1[f"partisipasi_{comp_year1}"] = (df_y1["pengguna"] / df_y1["dpt"]) * 100.0
                            df_y1_clean = df_y1[["kecamatan", f"partisipasi_{comp_year1}"]]
                            
                            df_y2[f"partisipasi_{comp_year2}"] = (df_y2["pengguna"] / df_y2["dpt"]) * 100.0
                            df_y2_clean = df_y2[["kecamatan", f"partisipasi_{comp_year2}"]]
                            
                            comp_df = pd.merge(df_y1_clean, df_y2_clean, on="kecamatan", how="outer")
                            
                            # Saring kecamatan sesuai pilihan filter di halaman
                            if selected_areas:
                                comp_df = comp_df[comp_df["kecamatan"].isin(selected_areas)]
                                
                            st.plotly_chart(dynamic_participation_comparison_chart(comp_df, comp_year1, comp_year2), use_container_width=True, theme=None)
                        else:
                            st.warning("Data perbandingan tidak tersedia.")
                    except Exception as e:
                        st.error(f"Gagal memuat perbandingan: {e}")
                
            st.markdown("---")
            st.markdown("### Statistik Sederhana")
            st.dataframe(
                filtered_df.select_dtypes(include='number').describe().T,
                use_container_width=True,
            )

# ------------------ TAB 2: SIMULASI PREDIKSI TPS ------------------
with tab_prediksi:
    st.markdown(f"### Form Pilihan Wilayah TPS (Tahun Pemilu {active_year})")
    st.info(f"Pilih Kecamatan, Kelurahan, dan TPS untuk memuat data parameter demografis tahun {active_year} secara otomatis dari database.")
    
    col_sel1, col_sel2, col_sel3 = st.columns(3)
    
    try:
        kec_df = get_all_kecamatan()
        kec_options = sorted(list(kec_df["nama_kecamatan"].unique()))
    except Exception:
        kec_options = []
        
    with col_sel1:
        kecamatan_val = st.selectbox("Kecamatan", options=kec_options)
        
    with col_sel2:
        if kecamatan_val:
            kel_options = get_kelurahannya_by_kecamatan(kecamatan_val, active_year)
        else:
            kel_options = []
        kelurahan_val = st.selectbox("Kelurahan", options=kel_options)
        
    with col_sel3:
        if kecamatan_val and kelurahan_val:
            tps_options = get_tps_by_kelurahan(kecamatan_val, kelurahan_val, active_year)
        else:
            tps_options = []
        no_tps_val = st.selectbox("Nomor TPS", options=tps_options)

    if kecamatan_val and kelurahan_val and no_tps_val:
        tps_data = get_tps_demographics(kecamatan_val, kelurahan_val, no_tps_val, active_year)
        
        if tps_data:
            st.markdown("---")
            st.markdown(f"#### Data Demografi Aktual: **TPS {no_tps_val} Kelurahan {kelurahan_val} (Kecamatan {kecamatan_val} - Tahun {active_year})**")
            
            # Tampilkan parameter dalam kolom sebagai informasi read-only
            col_d1, col_d2, col_d3 = st.columns(3)
            with col_d1:
                st.markdown(f"**Jumlah DPT TPS:** {int(tps_data['dpt']):,}".replace(",", "."))
                st.markdown(f"**Rasio DPT Kelurahan:** {tps_data['rasio_dpt_terhadap_penduduk_kelurahan']:.4f}")
                st.markdown(f"**Pendapatan Per Kapita:** Rp {tps_data['pendapatan_per_kapita']:,.0f}".replace(",", "."))
            with col_d2:
                st.markdown(f"**Tingkat Pengangguran:** {tps_data['tingkat_pengangguran']:.2f}%")
                st.markdown(f"**Kepadatan Penduduk:** {tps_data['kepadatan_penduduk']:.2f} jiwa/km²")
                st.markdown(f"**IPM Kecamatan:** {tps_data['ipm']:.2f}")
            with col_d3:
                st.markdown(f"**Proporsi Usia 17-24:** {tps_data['persen_usia_17_24_kec']:.2f}%")
                st.markdown(f"**Proporsi Usia 25-44:** {tps_data['persen_usia_25_44_kec']:.2f}%")
                st.markdown(f"**Proporsi Usia 45+:** {tps_data['persen_usia_45_plus_kec']:.2f}%")
                
            st.markdown("---")
            
            # Jalankan prediksi
            if st.button("Jalankan Prediksi Partisipasi Politik", use_container_width=True, type="primary"):
                input_values = {
                    "kecamatan": kecamatan_val,
                    "kelurahan": kelurahan_val,
                    "no_tps": no_tps_val,
                    "tahun": active_year,
                    "tahun_pemilu": active_year,
                    "dpt": tps_data['dpt'],
                    "rasio_dpt_terhadap_penduduk_kelurahan": tps_data['rasio_dpt_terhadap_penduduk_kelurahan'],
                    "pendapatan_per_kapita": tps_data['pendapatan_per_kapita'],
                    "tingkat_pengangguran": tps_data['tingkat_pengangguran'],
                    "kepadatan_penduduk": tps_data['kepadatan_penduduk'],
                    "ipm": tps_data['ipm'],
                    "persen_usia_17_24_kec": tps_data['persen_usia_17_24_kec'],
                    "persen_usia_25_44_kec": tps_data['persen_usia_25_44_kec'],
                    "persen_usia_45_plus_kec": tps_data['persen_usia_45_plus_kec'],
                }
                
                prediction = predict_participation(model_result.model, input_values)
                
                # Simpan ke database hasil prediksi
                try:
                    save_prediction({
                        "kecamatan": kecamatan_val,
                        "kelurahan": kelurahan_val,
                        "no_tps": no_tps_val,
                        "dpt": tps_data['dpt'],
                        "rasio_dpt_terhadap_penduduk_kelurahan": tps_data['rasio_dpt_terhadap_penduduk_kelurahan'],
                        "pendapatan_per_kapita": tps_data['pendapatan_per_kapita'],
                        "tingkat_pengangguran": tps_data['tingkat_pengangguran'],
                        "kepadatan_penduduk": tps_data['kepadatan_penduduk'],
                        "ipm": tps_data['ipm'],
                        "persen_usia_17_24_kec": tps_data['persen_usia_17_24_kec'],
                        "persen_usia_25_44_kec": tps_data['persen_usia_25_44_kec'],
                        "persen_usia_45_plus_kec": tps_data['persen_usia_45_plus_kec'],
                        "hasil_prediksi": prediction
                    })
                    st.success("Hasil prediksi berhasil disimpan ke database!")
                except Exception as e:
                    st.warning(f"Gagal menyimpan riwayat ke database: {e}")
                
                # Hasil Card
                st.markdown(
                    f"""
                    <div class="prediction-card" style="background-color: #ffffff; padding: 25px; border-radius: 12px; box-shadow: 0 4px 10px rgba(0,0,0,0.05); border-left: 6px solid #ff7f66; margin: 15px 0;">
                        <div class="prediction-title" style="font-weight: 800; font-size: 1rem; color: #64748b; text-transform: uppercase; margin-bottom: 5px;">Hasil Prediksi Partisipasi Politik ({active_year})</div>
                        <div style="font-size: 2.8rem; font-weight: 800; color: #ff7f66; line-height: 1.2;">
                            {prediction:.2f}%
                        </div>
                        <p style="margin: 5px 0 0 0; font-size: 0.95rem; color: #334155;">
                            Estimasi keikutsertaan pemilih di TPS {no_tps_val} Kelurahan {kelurahan_val.upper()} (Kecamatan {kecamatan_val}) untuk Pemilu {active_year}
                        </p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                
                # PDF Unduhan
                try:
                    pdf_data = {
                        "kecamatan": kecamatan_val,
                        "kelurahan": kelurahan_val,
                        "no_tps": no_tps_val,
                        "dpt": tps_data['dpt'],
                        "rasio_dpt": tps_data['rasio_dpt_terhadap_penduduk_kelurahan'],
                        "pendapatan_per_kapita": tps_data['pendapatan_per_kapita'],
                        "tingkat_pengangguran": tps_data['tingkat_pengangguran'],
                        "kepadatan_penduduk": tps_data['kepadatan_penduduk'],
                        "ipm": tps_data['ipm'],
                        "usia_17_24": tps_data['persen_usia_17_24_kec'],
                        "usia_25_44": tps_data['persen_usia_25_44_kec'],
                        "usia_45_plus": tps_data['persen_usia_45_plus_kec'],
                        "hasil_prediksi": prediction,
                        "model_metrics": {
                            "rmse": model_result.rmse,
                            "mae": model_result.mae,
                            "r2": model_result.r2
                        },
                        "printed_by": st.session_state.get("username", "Guest")
                    }
                    pdf_bytes = generate_recap_pdf(pdf_data)
                    st.download_button(
                        label="Unduh Rekap PDF Laporan",
                        data=pdf_bytes,
                        file_name=f"rekap_prediksi_{kelurahan_val.replace(' ', '_')}_tps{no_tps_val}_{active_year}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
                except Exception as pdf_err:
                    st.error(f"Gagal menyiapkan file PDF: {pdf_err}")
        else:
            st.error(f"Data untuk TPS terpilih di tahun {active_year} tidak tersedia.")

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
                "rasio_dpt_terhadap_penduduk_kelurahan": "Rasio DPT",
                "pendapatan_per_kapita": "Pendapatan",
                "tingkat_pengangguran": "Pengangguran (%)",
                "kepadatan_penduduk": "Kepadatan",
                "ipm": "IPM",
                "persen_usia_17_24_kec": "Usia 17-24 (%)",
                "persen_usia_25_44_kec": "Usia 25-44 (%)",
                "persen_usia_45_plus_kec": "Usia 45+ (%)",
                "hasil_prediksi": "Hasil Prediksi (%)",
                "created_at": "Tanggal Analisa"
            })
            display_history["Hasil Prediksi (%)"] = display_history["Hasil Prediksi (%)"].apply(lambda x: f"{x:.2f}%" if isinstance(x, (int, float)) else x)
            st.dataframe(display_history, use_container_width=True, hide_index=True)
    except Exception as e:
        st.error(f"Gagal memuat riwayat prediksi: {e}")

# ------------------ TAB 3: EVALUASI KINERJA MODEL ------------------
with tab_evaluasi:
    st.markdown(f"### Kinerja dan Evaluasi Model Random Forest (Data Tahun {active_year})")
    st.markdown(f"Berikut adalah hasil pengukuran keandalan model regresi yang dilatih menggunakan data TPS Pemilu tahun {active_year}.")
    
    # 1. Metrik evaluasi model
    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    col_m1.metric("RMSE Model", f"{model_result.rmse:.4f}", help="Root Mean Squared Error (makin kecil makin bagus)")
    col_m2.metric("MAE Model", f"{model_result.mae:.4f}", help="Mean Absolute Error (makin kecil makin bagus)")
    col_m3.metric("R² Score", f"{model_result.r2:.4f} ({model_result.r2*100:.1f}%)", help="Koefisien Determinasi (makin mendekati 1.0/100% makin bagus)")
    col_m4.metric("Jumlah Sampel Latih", len(df_train), help=f"Total data TPS {active_year} yang digunakan untuk model")
    
    st.markdown("---")
    
    # 2. Grafik visualisasi kinerja model
    col_g1, col_g2 = st.columns(2)
    with col_g1:
        st.plotly_chart(feature_importance_bar(model_result.feature_importance), use_container_width=True, theme=None)
        st.caption("Feature importance menunjukkan variabel demografi mana saja yang memiliki pengaruh paling signifikan terhadap tingkat partisipasi politik.")
    with col_g2:
        st.plotly_chart(prediction_scatter(model_result.prediction_result), use_container_width=True, theme=None)
        st.caption("Grafik tebaran (scatter plot) perbandingan antara nilai partisipasi aktual dengan hasil prediksi tebakan model.")
        
    # 3. Tabel Detail Prediksi vs Aktual
    st.markdown("---")
    st.markdown("#### Tabel Perbandingan Aktual vs Prediksi (Sampel Data Uji)")
    st.dataframe(model_result.prediction_result, use_container_width=True, hide_index=True)
