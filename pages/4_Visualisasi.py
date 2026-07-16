import streamlit as st
import pandas as pd
import subprocess
import sys

# Patch Popen to hide background terminal window popup on Windows (fixes Kaleido command prompt flash)
if sys.platform == "win32":
    orig_popen = subprocess.Popen
    def patched_popen(*args, **kwargs):
        # 0x08000000 is CREATE_NO_WINDOW
        kwargs["creationflags"] = kwargs.get("creationflags", 0) | 0x08000000
        return orig_popen(*args, **kwargs)
    subprocess.Popen = patched_popen

from src.data_loader import load_geojson, get_comparison_2019_2024
from src.ui import load_data_from_sidebar, render_header, setup_page
from src.visualizations import (
    correlation_heatmap,
    participation_map,
    participation_by_area,
    participation_comparison_chart,
)

setup_page("Visualisasi")
render_header("Visualisasi", "Grafik korelasi, peta spasial, dan perbandingan historis pemilu.")

# Memuat data dari database
df = load_data_from_sidebar()
if df.empty:
    st.warning("Database kosong atau belum diinisialisasi. Hubungi Admin untuk mengunggah CSV data awal.")
    st.stop()

# Menampilkan filter Tahun dan Kecamatan di halaman utama (page-level)
col_f1, col_f2 = st.columns(2)
with col_f1:
    years = sorted(df["tahun"].dropna().astype(int).unique().tolist())
    default_index = years.index(2024) if 2024 in years else len(years) - 1
    selected_year = st.selectbox("Pilih Tahun Pemilu", years, index=default_index, key="vis_tahun")
with col_f2:
    areas = sorted(df["kecamatan"].dropna().unique().tolist())
    selected_areas = st.multiselect("Filter Kecamatan", areas, key="vis_kecamatan")

# Menyaring data sesuai pilihan di halaman utama
filtered_df = df[df["tahun"] == selected_year]
if selected_areas:
    filtered_df = filtered_df[filtered_df["kecamatan"].isin(selected_areas)]

if filtered_df.empty:
    st.warning("Data kosong setelah filter.")
    st.stop()

# Inisialisasi variabel gambar grafik untuk PDF
fig_corr = None
fig_area = None
fig_comp = None

# 1. Menampilkan Peta Panas (Heatmap Korelasi)
st.markdown("### Korelasi Variabel Demografi & Partisipasi Politik")
fig_corr = correlation_heatmap(filtered_df)
st.plotly_chart(fig_corr, use_container_width=True, theme=None)
st.caption("Matriks korelasi Pearson menunjukkan arah dan kekuatan hubungan linier antara 9 fitur demografi dengan persentase partisipasi politik.")

# Buang data partisipasi yang kosong/NaN agar tidak error saat digambar grafiknya
chart_df = filtered_df.dropna(subset=["partisipasi_politik"])

if chart_df.empty:
    st.warning("Data partisipasi politik belum tersedia.")
else:
    # 2. Menampilkan grafik batang rata-rata partisipasi per kecamatan
    st.markdown("---")
    st.markdown(f"### Rata-rata Partisipasi Politik Pemilu {selected_year} per Kecamatan")
    fig_area = participation_by_area(chart_df)
    st.plotly_chart(fig_area, use_container_width=True, theme=None)

    # 3. Menampilkan grafik perbandingan historis dinamis
    st.markdown("---")
    st.markdown("### Grafik Perbandingan Historis Antar-Pemilu")
    
    col_vis_y1, col_vis_y2 = st.columns(2)
    all_years = sorted(df["tahun"].dropna().astype(int).unique().tolist())
    with col_vis_y1:
        comp_year1 = st.selectbox("Pilih Tahun Pemilu Pertama (Y1)", all_years, index=0, key="vis_comp_y1")
    with col_vis_y2:
        idx_default_y2 = all_years.index(2024) if 2024 in all_years else len(all_years) - 1
        comp_year2 = st.selectbox("Pilih Tahun Pemilu Kedua (Y2)", all_years, index=idx_default_y2, key="vis_comp_y2")
        
    if comp_year1 == comp_year2:
        st.warning("Silakan pilih dua tahun pemilu yang berbeda untuk melihat perbandingan.")
    else:
        from src.database import get_connection
        from src.visualizations import dynamic_participation_comparison_chart
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
                
                # Saring kecamatan sesuai filter di halaman
                if selected_areas:
                    comp_df = comp_df[comp_df["kecamatan"].isin(selected_areas)]
                    
                fig_comp = dynamic_participation_comparison_chart(comp_df, comp_year1, comp_year2)
                st.plotly_chart(fig_comp, use_container_width=True, theme=None)
            else:
                st.warning("Data perbandingan tidak tersedia.")
        except Exception as e:
            st.error(f"Gagal memuat perbandingan: {e}")

    # 4. Menampilkan Peta Partisipasi Politik
    st.markdown("---")
    st.markdown("### Peta Partisipasi Politik")
    years = sorted(chart_df["tahun"].dropna().astype(int).unique().tolist())
    if not years:
        st.warning("Data partisipasi politik untuk peta belum tersedia.")
    else:
        selected_map_year = st.selectbox("Pilih tahun peta", years, index=len(years) - 1)
        try:
            geojson = load_geojson()
            st.plotly_chart(participation_map(chart_df, geojson, selected_map_year), use_container_width=True, theme=None)
            st.caption(f"Peta spasial di atas mengagregasikan data TPS pemilu {selected_map_year} ke tingkat kecamatan secara dinamis agar sesuai dengan batas wilayah GeoJSON.")
        except Exception as error:
            st.warning(f"Peta gagal dimuat: {error}")

    # 5. Download Button for Laporan Analisis Lengkap (PDF)
    st.markdown("---")
    st.markdown("### Unduh Laporan Visualisasi dan Analisis")
    st.info("Anda dapat mengunduh seluruh hasil analisis visualisasi, matriks korelasi demografi, dan tren perbandingan historis lengkap beserta interpretasi akademisnya dalam format PDF.")
    
    # Initialize session state for PDF bytes
    if "vis_pdf_bytes" not in st.session_state:
        st.session_state["vis_pdf_bytes"] = None
        st.session_state["vis_pdf_year"] = None
        st.session_state["vis_pdf_areas"] = None
        st.session_state["vis_pdf_comp1"] = None
        st.session_state["vis_pdf_comp2"] = None

    # Check if parameters changed to invalidate old PDF cache
    params_match = (
        st.session_state["vis_pdf_year"] == selected_year and
        st.session_state["vis_pdf_areas"] == selected_areas and
        st.session_state["vis_pdf_comp1"] == comp_year1 and
        st.session_state["vis_pdf_comp2"] == comp_year2
    )

    if not params_match:
        st.session_state["vis_pdf_bytes"] = None

    if st.session_state["vis_pdf_bytes"] is None:
        if st.button("Proses dan Siapkan Laporan PDF", use_container_width=True, type="primary"):
            with st.spinner("Sedang merender grafik Plotly menjadi gambar dan menyusun laporan PDF..."):
                # 5a. Hitung data korelasi untuk PDF
                try:
                    from src.config import FEATURE_COLUMNS, TARGET_COLUMN
                    corr_cols = [*FEATURE_COLUMNS, TARGET_COLUMN]
                    corr_series = filtered_df[corr_cols].corr(numeric_only=True)[TARGET_COLUMN].drop(TARGET_COLUMN)
                    correlation_data = [{"variabel": var, "korelasi": val} for var, val in corr_series.items()]
                except Exception:
                    correlation_data = []
                    
                # 5b. Hitung rata-rata partisipasi per kecamatan untuk PDF
                try:
                    avg_df = filtered_df.groupby("kecamatan", as_index=False)["partisipasi_politik"].mean().sort_values("partisipasi_politik", ascending=False)
                    average_data = avg_df.to_dict(orient="records")
                except Exception:
                    average_data = []
                    
                # 5c. Hitung data perbandingan untuk PDF
                comparison_data = []
                try:
                    if comp_year1 != comp_year2:
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
                            comp_df_pdf = pd.merge(df_y1_clean, df_y2_clean, on="kecamatan", how="outer")
                            if selected_areas:
                                comp_df_pdf = comp_df_pdf[comp_df_pdf["kecamatan"].isin(selected_areas)]
                            comp_df_pdf["selisih"] = comp_df_pdf[f"partisipasi_{comp_year2}"] - comp_df_pdf[f"partisipasi_{comp_year1}"]
                            comparison_data = comp_df_pdf.to_dict(orient="records")
                except Exception:
                    pass
                
                # 5d. Buat berkas gambar sementara
                try:
                    import tempfile
                    import os
                    
                    path_corr = None
                    path_area = None
                    path_comp = None
                    tmp_files = []
                    
                    def save_fig_to_temp(fig):
                        if fig is None: return None
                        try:
                            img_bytes = fig.to_image(format="png", width=600, height=400, engine="kaleido")
                            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
                            tmp.write(img_bytes)
                            tmp.close()
                            tmp_files.append(tmp.name)
                            return tmp.name
                        except Exception as e:
                            import sys
                            print(f"Error saving temp fig: {e}", file=sys.stderr)
                            return None
                            
                    if fig_corr: path_corr = save_fig_to_temp(fig_corr)
                    if fig_area: path_area = save_fig_to_temp(fig_area)
                    if fig_comp: path_comp = save_fig_to_temp(fig_comp)
                    
                    from src.pdf_generator import generate_visualization_pdf
                    pdf_data = {
                        "active_year": selected_year,
                        "selected_areas": selected_areas,
                        "correlation_data": correlation_data,
                        "average_data": average_data,
                        "comparison_year1": comp_year1,
                        "comparison_year2": comp_year2,
                        "comparison_data": comparison_data,
                        "path_corr": path_corr,
                        "path_area": path_area,
                        "path_comp": path_comp,
                        "printed_by": st.session_state.get("username", "Guest")
                    }
                    pdf_bytes = generate_visualization_pdf(pdf_data)
                    
                    # Clean up temp files
                    for f in tmp_files:
                        try:
                            os.unlink(f)
                        except Exception:
                            pass
                            
                    st.session_state["vis_pdf_bytes"] = pdf_bytes
                    st.session_state["vis_pdf_year"] = selected_year
                    st.session_state["vis_pdf_areas"] = selected_areas
                    st.session_state["vis_pdf_comp1"] = comp_year1
                    st.session_state["vis_pdf_comp2"] = comp_year2
                    st.success("Laporan PDF berhasil disiapkan!")
                    st.rerun()
                except Exception as pdf_err:
                    st.error(f"Gagal menyiapkan file PDF laporan: {pdf_err}")
    else:
        # PDF is ready, show download button!
        st.download_button(
            "Unduh Laporan Analisis Lengkap (PDF)",
            data=st.session_state["vis_pdf_bytes"],
            file_name=f"laporan_analisis_visualisasi_{selected_year}.pdf",
            mime="application/pdf",
            use_container_width=True,
            type="primary"
        )


