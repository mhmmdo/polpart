import streamlit as st
import pandas as pd
import sqlite3

from src.ui import render_header, setup_page
from src.data_loader import load_dataset
from src.config import DB_PATH
from src.database import (
    get_all_kecamatan,
    get_kelurahannya_by_kecamatan,
    get_tps_by_kelurahan,
    get_tps_demographics,
    add_tps_record,
    update_tps_record,
    delete_tps_record,
    add_partai,
    delete_partai,
    update_partai
)

setup_page("Dashboard")

# Periksa hak akses peran pengguna
role = st.session_state.get("role", "user")

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

# ------------------ SEKSI MANAJEMEN DATA ADMIN (COLLAPSED EXPANDER) ------------------
if role == "admin":
    st.markdown("---")
    with st.expander("Manajemen Basis Data Pemilu (Khusus Admin)"):
        # Radio Selector untuk menu admin
        admin_menu = st.radio("Pilih Menu Manajemen", ["Impor CSV", "Kelola Partai", "Kelola TPS"], horizontal=True)
        
        # 1. Menu Impor CSV
        if admin_menu == "Impor CSV":
            st.markdown("#### Impor Dataset Pemilu KPU")
            st.warning("Mengunggah file baru akan memperbarui data untuk tahun pemilu yang terdapat di dalam berkas CSV.")
            
            uploaded_file = st.file_uploader("Pilih file CSV dataset KPU tingkat TPS", type=["csv"], key="dashboard_csv_uploader")
            
            if uploaded_file is not None:
                try:
                    import_df = pd.read_csv(uploaded_file)
                    import_df.columns = (
                        import_df.columns.astype(str)
                        .str.strip()
                        .str.lower()
                        .str.replace(" ", "_", regex=False)
                        .str.replace("-", "_", regex=False)
                    )
                    
                    required = ["tahun_pemilu", "kecamatan", "kelurahan", "no_tps", "partisipasi_politik"]
                    missing = [c for c in required if c not in import_df.columns]
                    
                    if missing:
                        st.error(f"Gagal Impor: Kolom wajib '{', '.join(missing)}' tidak ditemukan di CSV.")
                    else:
                        success_count = 0
                        skipped_count = 0
                        
                        from src.database import get_connection, seed_relational_tables_from_tps
                        
                        with get_connection() as conn:
                            cursor = conn.cursor()
                            # Hanya hapus data untuk tahun pemilu yang ada di dalam berkas CSV yang diunggah
                            years_in_csv = [int(float(y)) for y in import_df["tahun_pemilu"].dropna().unique().tolist()]
                            for y in years_in_csv:
                                cursor.execute("DELETE FROM data_partisipasi_tps WHERE tahun_pemilu = ?", (y,))
                            
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
                                
                                pendapatan = clean_float(row.get("pendapatan_per_kapita"))
                                pengangguran = clean_float(row.get("tingkat_pengangguran"))
                                kepadatan = clean_float(row.get("kepadatan_penduduk"))
                                ipm = clean_float(row.get("ipm"))
                                
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
                                        f"{tahun}-{kec}-{kel}-{tps}".strip().upper(),
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
                            
                            # Sync relational tables
                            seed_relational_tables_from_tps()
                            
                        st.success(f"Berhasil impor {success_count} data!")
                        st.rerun()
                except Exception as e:
                    st.error(f"Gagal memproses berkas: {e}")

        # 2. Menu Kelola Partai
        elif admin_menu == "Kelola Partai":
            st.markdown("#### Kelola Partai Politik")
            opt_partai = st.radio("Pilih Tindakan", ["Tambah Partai Baru", "Edit Partai", "Hapus Partai"], horizontal=True)
            
            if opt_partai == "Tambah Partai Baru":
                st.markdown("##### Tambah Partai Politik Baru")
                with st.form("add_partai_db_form"):
                    no_urut_p = st.number_input("Nomor Urut", min_value=1, max_value=100, value=1)
                    singkatan_p = st.text_input("Singkatan Partai (Contoh: GOLKAR, PDIP)", max_chars=15)
                    nama_p = st.text_input("Nama Lengkap Partai Politik")
                    submit_add_p = st.form_submit_button("Simpan Partai Baru", use_container_width=True)
                    
                    if submit_add_p:
                        if not singkatan_p.strip() or not nama_p.strip():
                            st.error("Gagal: Singkatan dan Nama Lengkap Partai tidak boleh kosong.")
                        else:
                            if add_partai(nama_p, singkatan_p, no_urut_p):
                                st.success(f"Berhasil menambahkan partai {singkatan_p.upper()}!")
                                st.rerun()
                            else:
                                st.error("Gagal: Partai dengan singkatan/nama/nomor urut tersebut sudah terdaftar.")
                                
            elif opt_partai == "Edit Partai":
                st.markdown("##### Edit Partai Politik Lama")
                try:
                    with sqlite3.connect(DB_PATH) as conn:
                        df_opts = pd.read_sql_query("SELECT id_partai, singkatan, nama_partai, nomor_urut FROM partai ORDER BY nomor_urut", conn)
                    options_edit = ["-- Pilih Partai untuk Diedit --"] + [f"{r['singkatan']} - {r['nama_partai']} (ID: {r['id_partai']})" for _, r in df_opts.iterrows()]
                except Exception:
                    options_edit = ["-- Pilih Partai untuk Diedit --"]
                    
                selected_edit_partai = st.selectbox("Pilih Partai", options_edit)
                
                if selected_edit_partai != "-- Pilih Partai untuk Diedit --":
                    p_id = int(selected_edit_partai.split("ID: ")[-1].replace(")", ""))
                    partai_details = df_opts[df_opts["id_partai"] == p_id].iloc[0]
                    
                    with st.form("edit_partai_db_form"):
                        no_urut_edit = st.number_input("Nomor Urut", min_value=1, value=int(partai_details["nomor_urut"]))
                        singkatan_edit = st.text_input("Singkatan Partai", value=str(partai_details["singkatan"]), max_chars=15)
                        nama_edit = st.text_input("Nama Lengkap Partai", value=str(partai_details["nama_partai"]))
                        submit_update_p = st.form_submit_button("Simpan Perubahan", use_container_width=True)
                        
                        if submit_update_p:
                            if not singkatan_edit.strip() or not nama_edit.strip():
                                st.error("Gagal: Singkatan dan Nama Lengkap tidak boleh kosong.")
                            else:
                                if update_partai(p_id, nama_edit, singkatan_edit, no_urut_edit):
                                    st.success("Perubahan data partai politik berhasil disimpan!")
                                    st.rerun()
                                else:
                                    st.error("Gagal memperbarui data partai. Pastikan tidak ada bentrokan nomor/singkatan.")
                                    
            elif opt_partai == "Hapus Partai":
                st.markdown("##### Hapus Partai Politik")
                st.warning("Menghapus partai politik akan menghapus seluruh data perolehan suara partai tersebut di seluruh TPS.")
                try:
                    with sqlite3.connect(DB_PATH) as conn:
                        df_opts = pd.read_sql_query("SELECT id_partai, singkatan, nama_partai FROM partai ORDER BY nomor_urut", conn)
                    options_del = ["-- Pilih Partai untuk Dihapus --"] + [f"{r['singkatan']} - {r['nama_partai']} (ID: {r['id_partai']})" for _, r in df_opts.iterrows()]
                except Exception:
                    options_del = ["-- Pilih Partai untuk Dihapus --"]
                    
                selected_del_partai = st.selectbox("Pilih Partai", options_del, key="partai_del_sel")
                submit_del_p = st.button("Hapus Partai Secara Permanen", use_container_width=True, type="primary")
                
                if submit_del_p:
                    if selected_del_partai == "-- Pilih Partai untuk Dihapus --":
                        st.error("Silakan pilih partai terlebih dahulu.")
                    else:
                        p_id = int(selected_del_partai.split("ID: ")[-1].replace(")", ""))
                        if delete_partai(p_id):
                            st.success("Partai politik berhasil dihapus dari database.")
                            st.rerun()
                        else:
                            st.error("Gagal menghapus partai dari database.")

        # 3. Menu Kelola TPS
        elif admin_menu == "Kelola TPS":
            st.markdown("#### Kelola Data TPS Pemilu")
            opt_tps = st.radio("Pilih Tindakan TPS", ["Tambah TPS Baru", "Edit TPS", "Hapus TPS"], horizontal=True)
            
            kec_options = ["BANJARMASIN BARAT", "BANJARMASIN SELATAN", "BANJARMASIN TIMUR", "BANJARMASIN TENGAH", "BANJARMASIN UTARA"]
            
            if opt_tps == "Tambah TPS Baru":
                st.markdown("##### Input Rekaman Data TPS Baru")
                with st.form("form_tambah_tps_db"):
                    col_tf1, col_tf2 = st.columns(2)
                    with col_tf1:
                        t_tahun = st.selectbox("Tahun Pemilu", [2019, 2024, 2029], index=1)
                        t_kec = st.selectbox("Kecamatan", kec_options)
                        t_kel = st.text_input("Kelurahan (Kapital)", value="BASIRIH").upper()
                        t_no_tps = st.text_input("Nomor TPS (3 Digit, contoh: 001, 012)", value="001")
                        t_dpt = st.number_input("Jumlah DPT TPS", min_value=1, value=250)
                        t_pilih = st.number_input("Pengguna Hak Pilih TPS", min_value=0, value=200)
                        t_rasio = st.number_input("Rasio DPT Kelurahan", min_value=0.0, value=1.20, step=0.01)
                        t_pendapatan = st.number_input("Pendapatan Per Kapita Kelurahan (Rp)", min_value=0.0, value=66989407.0, step=10000.0)
                    with col_tf2:
                        t_pengangguran = st.number_input("Tingkat Pengangguran (%)", min_value=0.0, value=6.56, step=0.01)
                        t_kepadatan = st.number_input("Kepadatan Penduduk (jiwa/km²)", min_value=0.0, value=10550.43, step=10.0)
                        t_ipm = st.number_input("IPM Kecamatan", min_value=0.0, value=80.53, step=0.01)
                        t_u17_24 = st.number_input("Pemilih Usia 17-24 Tahun (%)", min_value=0.0, value=13.6, step=0.1)
                        t_u25_44 = st.number_input("Pemilih Usia 25-44 Tahun (%)", min_value=0.0, value=29.7, step=0.1)
                        t_u45_plus = st.number_input("Pemilih Usia 45+ Tahun (%)", min_value=0.0, value=32.2, step=0.1)
                    
                    submit_add_tps = st.form_submit_button("Simpan TPS Baru", use_container_width=True)
                    
                    if submit_add_tps:
                        if not t_kel.strip() or not t_no_tps.strip():
                            st.error("Gagal: Nama Kelurahan dan Nomor TPS wajib diisi.")
                        elif t_pilih > t_dpt:
                            st.error("Gagal: Pengguna hak pilih tidak boleh melebihi Jumlah DPT.")
                        else:
                            new_data = {
                                "tahun_pemilu": t_tahun,
                                "kecamatan": t_kec,
                                "kelurahan": t_kel.strip().upper(),
                                "no_tps": t_no_tps.strip(),
                                "dpt": t_dpt,
                                "pengguna_hak_pilih": t_pilih,
                                "rasio_dpt_terhadap_penduduk_kelurahan": t_rasio,
                                "pendapatan_per_kapita": t_pendapatan,
                                "tingkat_pengangguran": t_pengangguran,
                                "kepadatan_penduduk": t_kepadatan,
                                "ipm": t_ipm,
                                "persen_usia_17_24_kec": t_u17_24,
                                "persen_usia_25_44_kec": t_u25_44,
                                "persen_usia_45_plus_kec": t_u45_plus
                            }
                            if add_tps_record(new_data):
                                st.success(f"Berhasil menyimpan data TPS {t_no_tps} Kelurahan {t_kel}!")
                                st.rerun()
                            else:
                                st.error("Gagal menyimpan TPS baru. Pastikan kombinasi Kecamatan-Kelurahan-TPS belum pernah terdaftar.")
                                
            elif opt_tps == "Edit TPS":
                st.markdown("##### Edit Data TPS")
                st.info("Pilih TPS yang ingin diubah terlebih dahulu:")
                
                col_es1, col_es2, col_es3 = st.columns(3)
                with col_es1:
                    try:
                        k_list = sorted(list(get_all_kecamatan()["nama_kecamatan"].unique()))
                    except Exception:
                        k_list = kec_options
                    edit_kec = st.selectbox("Kecamatan", k_list, key="edit_kec_sel")
                with col_es2:
                    el_options = get_kelurahannya_by_kecamatan(edit_kec)
                    edit_kel = st.selectbox("Kelurahan", el_options, key="edit_kel_sel")
                with col_es3:
                    et_options = get_tps_by_kelurahan(edit_kec, edit_kel)
                    edit_no_tps = st.selectbox("Nomor TPS", et_options, key="edit_tps_sel")
                    
                if edit_kec and edit_kel and edit_no_tps:
                    tps_raw = get_tps_demographics(edit_kec, edit_kel, edit_no_tps)
                    
                    if tps_raw:
                        with st.form("form_edit_tps_db"):
                            st.markdown(f"**Ubah Parameter TPS {edit_no_tps} Kelurahan {edit_kel}**")
                            col_ef1, col_ef2 = st.columns(2)
                            with col_ef1:
                                e_tahun = st.selectbox("Tahun Pemilu", [2019, 2024, 2029], index=[2019, 2024, 2029].index(tps_raw["tahun_pemilu"]))
                                e_dpt = st.number_input("Jumlah DPT TPS", min_value=1, value=int(tps_raw["dpt"]))
                                e_pilih = st.number_input("Pengguna Hak Pilih TPS", min_value=0, value=int(tps_raw["pengguna_hak_pilih"]))
                                e_rasio = st.number_input("Rasio DPT Kelurahan", min_value=0.0, value=float(tps_raw["rasio_dpt_terhadap_penduduk_kelurahan"]), step=0.01)
                                e_pendapatan = st.number_input("Pendapatan Per Kapita Kelurahan (Rp)", min_value=0.0, value=float(tps_raw["pendapatan_per_kapita"]), step=10000.0)
                            with col_ef2:
                                e_pengangguran = st.number_input("Tingkat Pengangguran (%)", min_value=0.0, value=float(tps_raw["tingkat_pengangguran"]), step=0.01)
                                e_kepadatan = st.number_input("Kepadatan Penduduk (jiwa/km²)", min_value=0.0, value=float(tps_raw["kepadatan_penduduk"]), step=10.0)
                                e_ipm = st.number_input("IPM Kecamatan", min_value=0.0, value=float(tps_raw["ipm"]), step=0.01)
                                e_u17_24 = st.number_input("Pemilih Usia 17-24 Tahun (%)", min_value=0.0, value=float(tps_raw["persen_usia_17_24_kec"]), step=0.1)
                                e_u25_44 = st.number_input("Pemilih Usia 25-44 Tahun (%)", min_value=0.0, value=float(tps_raw["persen_usia_25_44_kec"]), step=0.1)
                                e_u45_plus = st.number_input("Pemilih Usia 45+ Tahun (%)", min_value=0.0, value=float(tps_raw["persen_usia_45_plus_kec"]), step=0.1)
                            
                            submit_edit_tps = st.form_submit_button("Simpan Perubahan Data TPS", use_container_width=True)
                            
                            if submit_edit_tps:
                                if e_pilih > e_dpt:
                                    st.error("Gagal: Pengguna hak pilih tidak boleh melebihi jumlah DPT.")
                                else:
                                    updated_data = {
                                        "tahun_pemilu": e_tahun,
                                        "kecamatan": edit_kec,
                                        "kelurahan": edit_kel,
                                        "no_tps": edit_no_tps,
                                        "dpt": e_dpt,
                                        "pengguna_hak_pilih": e_pilih,
                                        "rasio_dpt_terhadap_penduduk_kelurahan": e_rasio,
                                        "pendapatan_per_kapita": e_pendapatan,
                                        "tingkat_pengangguran": e_pengangguran,
                                        "kepadatan_penduduk": e_kepadatan,
                                        "ipm": e_ipm,
                                        "persen_usia_17_24_kec": e_u17_24,
                                        "persen_usia_25_44_kec": e_u25_44,
                                        "persen_usia_45_plus_kec": e_u45_plus
                                    }
                                    if update_tps_record(tps_raw["id"], updated_data):
                                        st.success("Perubahan data TPS berhasil disimpan!")
                                        st.rerun()
                                    else:
                                        st.error("Gagal memperbarui data TPS di database.")
                                        
            elif opt_tps == "Hapus TPS":
                st.markdown("##### Hapus Rekaman Data TPS")
                st.warning("Penghapusan data TPS ini bersifat permanen.")
                
                col_ds1, col_ds2, col_ds3 = st.columns(3)
                with col_ds1:
                    try:
                        k_list = sorted(list(get_all_kecamatan()["nama_kecamatan"].unique()))
                    except Exception:
                        k_list = kec_options
                    del_kec = st.selectbox("Kecamatan", k_list, key="del_kec_sel")
                with col_ds2:
                    dl_options = get_kelurahannya_by_kecamatan(del_kec)
                    del_kel = st.selectbox("Kelurahan", dl_options, key="del_kel_sel")
                with col_ds3:
                    dt_options = get_tps_by_kelurahan(del_kec, del_kel)
                    del_no_tps = st.selectbox("Nomor TPS", dt_options, key="del_tps_sel")
                    
                if del_kec and del_kel and del_no_tps:
                    tps_raw = get_tps_demographics(del_kec, del_kel, del_no_tps)
                    if tps_raw:
                        submit_del_tps = st.button("Hapus TPS Secara Permanen", use_container_width=True, type="primary")
                        if submit_del_tps:
                            if delete_tps_record(tps_raw["id"]):
                                st.success("Data TPS berhasil dihapus permanen.")
                                st.rerun()
                            else:
                                st.error("Gagal menghapus data TPS dari database.")

