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
    # Only display file uploader to logged-in Admin
    if st.session_state.get("role") == "admin":
        uploaded_file = st.sidebar.file_uploader("Unggah File CSV untuk Impor Baru", type=["csv"], key="sidebar_csv_uploader_ui")
        if uploaded_file is not None:
            try:
                import pandas as pd
                import_df = pd.read_csv(uploaded_file)
                
                # Standardize columns
                import_df.columns = (
                    import_df.columns.astype(str)
                    .str.strip()
                    .str.lower()
                    .str.replace(" ", "_", regex=False)
                    .str.replace("-", "_", regex=False)
                )
                
                # Check required columns
                required = ["tahun_pemilu", "kecamatan", "kelurahan", "no_tps", "partisipasi_politik"]
                missing_cols = [c for c in required if c not in import_df.columns]
                
                if missing_cols:
                    st.sidebar.error(f"Gagal: Kolom '{', '.join(missing_cols)}' wajib ada.")
                else:
                    success_count = 0
                    skipped_count = 0
                    
                    from src.database import get_connection
                    
                    with get_connection() as conn:
                        cursor = conn.cursor()
                        # Clear old data before importing new CSV
                        cursor.execute("DELETE FROM data_partisipasi_tps")
                        
                        for idx, row in import_df.iterrows():
                            tahun = row.get("tahun_pemilu")
                            kec = row.get("kecamatan")
                            kel = row.get("kelurahan")
                            tps = row.get("no_tps")
                            
                            if pd.isna(tahun) or pd.isna(kec) or pd.isna(kel) or pd.isna(tps):
                                skipped_count += 1
                                continue
                                
                            def clean_float(val):
                                try:
                                    if pd.isna(val): return None
                                    if isinstance(val, str): val = val.replace(",", "")
                                    return float(val)
                                except Exception:
                                    return None
                                    
                            def clean_int(val):
                                try:
                                    if pd.isna(val): return None
                                    if isinstance(val, str): val = val.replace(",", "")
                                    return int(float(val))
                                except Exception:
                                    return None
                            
                            dpt = clean_int(row.get("dpt"))
                            pilih = clean_int(row.get("pengguna_hak_pilih"))
                            partisipasi = clean_float(row.get("partisipasi_politik"))
                            dpt_total = clean_int(row.get("dpt_total_tps"))
                            
                            penduduk_kel = row.get("penduduk_total_kelurahan")
                            if pd.isna(penduduk_kel):
                                penduduk_kel = None
                            else:
                                penduduk_kel = str(penduduk_kel).strip()
                                
                            pend_kec = clean_int(row.get("penduduk_total_kecamatan"))
                            rasio_dpt = clean_float(row.get("rasio_dpt_terhadap_penduduk_kelurahan"))
                            
                            # Socio-economic columns
                            pendapatan = clean_float(row.get("pendapatan_per_kapita"))
                            pengangguran = clean_float(row.get("tingkat_pengangguran"))
                            kepadatan = clean_float(row.get("kepadatan_penduduk"))
                            ipm = clean_float(row.get("ipm"))
                            
                            # Age distributions
                            j_usia_17_24 = clean_int(row.get("jumlah_usia_17_24_kec"))
                            j_usia_25_44 = clean_int(row.get("jumlah_usia_25_44_kec"))
                            j_usia_45_plus = clean_int(row.get("jumlah_usia_45_plus_kec"))
                            
                            u17_24 = clean_float(row.get("persen_usia_17_24_kec"))
                            u25_44 = clean_float(row.get("persen_usia_25_44_kec"))
                            u45_plus = clean_float(row.get("persen_usia_45_plus_kec"))
                            
                            try:
                                cursor.execute("""
                                    INSERT INTO data_partisipasi_tps (
                                        tahun_pemilu, level_data, kecamatan, kelurahan, no_tps, id_record,
                                        dpt, pengguna_hak_pilih, partisipasi_politik, dpt_total_tps,
                                        penduduk_total_kelurahan, penduduk_total_kecamatan, rasio_dpt_terhadap_penduduk_kelurahan,
                                        pendapatan_per_kapita, tingkat_pengangguran, kepadatan_penduduk, ipm,
                                        jumlah_usia_17_24_kec, jumlah_usia_25_44_kec, jumlah_usia_45_plus_kec,
                                        persen_usia_17_24_kec, persen_usia_25_44_kec, persen_usia_45_plus_kec
                                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                                """, (
                                    int(tahun),
                                    'tps',
                                    str(kec).strip().upper(),
                                    str(kel).strip().upper(),
                                    str(tps).strip(),
                                    row.get("id_record"),
                                    dpt,
                                    pilih,
                                    partisipasi,
                                    dpt_total,
                                    penduduk_kel,
                                    pend_kec,
                                    rasio_dpt,
                                    pendapatan,
                                    pengangguran,
                                    kepadatan,
                                    ipm,
                                    j_usia_17_24,
                                    j_usia_25_44,
                                    j_usia_45_plus,
                                    u17_24,
                                    u25_44,
                                    u45_plus
                                ))
                                success_count += 1
                            except Exception:
                                skipped_count += 1
                                
                        conn.commit()
                        
                        # Sync new relational tables
                        from src.database import seed_relational_tables_from_tps
                        seed_relational_tables_from_tps()
                        
                    st.sidebar.success(f"Berhasil impor {success_count} data!")
                    st.rerun()
            except Exception as e:
                st.sidebar.error(f"Gagal memproses berkas: {e}")
    else:
        st.sidebar.info("Akses unggah CSV dinonaktifkan untuk akun Masyarakat.")
        
    from src.data_loader import load_dataset
    return load_dataset()


def sidebar_filters(df):
    years = sorted(df["tahun"].dropna().astype(int).unique().tolist())
    areas = sorted(df["kecamatan"].dropna().unique().tolist())

    selected_years = st.sidebar.multiselect("Filter tahun", years, key="filter_tahun_clean")
    selected_areas = st.sidebar.multiselect("Filter kecamatan", areas, key="filter_kecamatan_clean")
    return selected_years, selected_areas


def metric_card(label: str, value: str, help_text: str | None = None):
    st.metric(label=label, value=value, help=help_text)
