"""
Modul untuk mengatur elemen antarmuka pengguna (UI) menggunakan Streamlit.
Berisi fungsi-fungsi untuk menampilkan header, kartu metrik (metric card),
dan sidebar untuk filter serta unggah data.
"""
import streamlit as st

from src.config import APP_SUBTITLE, APP_TITLE, STYLE_PATH
from src.data_loader import load_dataset


def setup_page(title: str = APP_TITLE):
    # Map title to navigation option
    title_mapping = {
        "Dashboard": "Dashboard",
        "Data Historis": "Data Historis",
        "Prediksi": "Prediksi",
        "Visualisasi": "Visualisasi",
        "Tentang": "Tentang"
    }
    st.session_state["current_page"] = title_mapping.get(title, "Dashboard")
    inject_css()


def inject_css():
    if STYLE_PATH.exists():
        st.html(f"<style>{STYLE_PATH.read_text(encoding='utf-8')}</style>")


def render_header(title: str, subtitle: str | None = None):
    html_content = f"""<div class="hero-container">
<div class="breadcrumb">BERANDA &nbsp;&rsaquo;&nbsp; {title}</div>
<h1 class="hero-title">{title}</h1>
<p class="hero-subtitle">{subtitle or ""}</p>
</div>"""
    st.html(html_content.replace("\n", " ").strip())


def custom_metric_card(header: str, value: str, icon: str = "", trend_text: str = "", trend_type: str = "up") -> str:
    if trend_type == "up":
        trend_class = "trend-up"
        badge_class = "badge-green"
    elif trend_type == "down":
        trend_class = "trend-down"
        badge_class = "badge-purple"
    else:
        trend_class = "trend-neutral"
        badge_class = "badge-orange"
        
    icon_html = f'<span class="card-badge {badge_class}">{icon}</span>' if icon else ''
    html_content = f"""<div class="dashboard-card">
<div class="card-header">{header}</div>
<div class="card-body">
<div class="card-row">
<span class="card-value">{value}</span>
{icon_html}
</div>
<div class="card-trend {trend_class}">{trend_text}</div>
</div>
</div>"""
    return html_content.replace("\n", " ").strip()


def load_data_from_sidebar():
    st.sidebar.markdown("### Dataset")
    
    if "uploader_reset_key" not in st.session_state:
        st.session_state["uploader_reset_key"] = 0
    uploaded_file = st.sidebar.file_uploader(
        "Unggah File CSV untuk Impor Data",
        type=["csv"],
        key=f"csv_uploader_{st.session_state.uploader_reset_key}",
        label_visibility="visible",
    )
    if uploaded_file is not None:
        try:
            import pandas as pd
            import_df = pd.read_csv(uploaded_file)
            
            import_df.columns = (
                import_df.columns.astype(str)
                .str.strip()
                .str.lower()
                .str.replace(" ", "_", regex=False)
                .str.replace("-", "_", regex=False)
            )
            
            required = ["tahun", "kecamatan"]
            missing_cols = [c for c in required if c not in import_df.columns]
            
            if missing_cols:
                st.sidebar.error(f"Gagal: Kolom '{', '.join(missing_cols)}' wajib ada.")
            else:
                success_count = 0
                skipped_count = 0
                
                from src.database import get_connection, get_kecamatan_id_by_name
                
                with get_connection() as conn:
                    cursor = conn.cursor()
                    for idx, row in import_df.iterrows():
                        tahun_val = row.get("tahun")
                        kec_val = row.get("kecamatan")
                        
                        if pd.isna(tahun_val) or pd.isna(kec_val) or str(kec_val).strip() == "":
                            skipped_count += 1
                            continue
                            
                        try:
                            tahun_val = int(float(tahun_val))
                            kec_val = str(kec_val).strip()
                        except Exception:
                            skipped_count += 1
                            continue
                            
                        try:
                            id_kec = get_kecamatan_id_by_name(conn, kec_val)
                            
                            def clean_float(val):
                                try:
                                    return float(val) if pd.notna(val) else None
                                except Exception:
                                    return None
                                    
                            tingkat_pendidikan = clean_float(row.get("tingkat_pendidikan"))
                            pendapatan_per_kapita = clean_float(row.get("pendapatan_per_kapita"))
                            tingkat_pengangguran = clean_float(row.get("tingkat_pengangguran"))
                            kepadatan_penduduk = clean_float(row.get("kepadatan_penduduk"))
                            ipm = clean_float(row.get("ipm"))
                            partisipasi_politik = clean_float(row.get("partisipasi_politik"))
                            
                            cursor.execute("""
                                INSERT INTO data_sosio_ekonomi (
                                    id_kecamatan, tahun, tingkat_pendidikan, pendapatan_per_kapita,
                                    tingkat_pengangguran, kepadatan_penduduk, ipm, created_at, updated_at
                                ) VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                                ON CONFLICT(id_kecamatan, tahun) DO UPDATE SET
                                    tingkat_pendidikan=excluded.tingkat_pendidikan,
                                    pendapatan_per_kapita=excluded.pendapatan_per_kapita,
                                    tingkat_pengangguran=excluded.tingkat_pengangguran,
                                    kepadatan_penduduk=excluded.kepadatan_penduduk,
                                    ipm=excluded.ipm,
                                    updated_at=CURRENT_TIMESTAMP
                            """, (
                                id_kec, tahun_val, tingkat_pendidikan, pendapatan_per_kapita,
                                tingkat_pengangguran, kepadatan_penduduk, ipm
                            ))
                            
                            cursor.execute("""
                                INSERT INTO data_partisipasi_politik (
                                    id_kecamatan, tahun, dpt, pengguna_hak_pilih,
                                    partisipasi_politik, sumber_data, created_at, updated_at
                                ) VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                                ON CONFLICT(id_kecamatan, tahun) DO UPDATE SET
                                    partisipasi_politik=excluded.partisipasi_politik,
                                    sumber_data=excluded.sumber_data,
                                    updated_at=CURRENT_TIMESTAMP
                            """, (
                                id_kec, tahun_val, None, None, partisipasi_politik, "Upload UI CSV"
                            ))
                            success_count += 1
                        except Exception as e:
                            skipped_count += 1
                            
                    conn.commit()
                st.session_state["uploader_reset_key"] += 1
                st.sidebar.success(f"Berhasil impor {success_count} data!")
                st.rerun()
        except Exception as e:
            st.sidebar.error(f"Gagal memproses berkas: {e}")
                
    return load_dataset()


def sidebar_filters(df):
    years = sorted(df["tahun"].dropna().astype(int).unique().tolist())
    areas = sorted(df["kecamatan"].dropna().unique().tolist())

    selected_years = st.sidebar.multiselect("Filter tahun", years, key="filter_tahun_clean")
    selected_areas = st.sidebar.multiselect("Filter kecamatan", areas, key="filter_kecamatan_clean")
    return selected_years, selected_areas


def metric_card(label: str, value: str, help_text: str | None = None):
    st.metric(label=label, value=value, help=help_text)
