import sys
from pathlib import Path
import pandas as pd
import numpy as np
import joblib

ROOT_DIR = Path("d:/TA/polpart")
sys.path.append(str(ROOT_DIR))

from src.database import get_connection

def generate_synthetic_data(num_samples=1000):
    print("--- MEMBACA DATA ASLI 2024 ---")
    with get_connection() as conn:
        df_real = pd.read_sql_query("""
            SELECT * FROM data_partisipasi_tps 
            WHERE tahun_pemilu = 2024 AND level_data = 'tps'
        """, conn)
        
    if df_real.empty:
        raise ValueError("Data asli 2024 tidak ditemukan di database. Pastikan data awal sudah diimpor.")
        
    print(f"Data asli ditemukan: {len(df_real)} baris.")
    
    # Bersihkan anomali pada data asli sebelum dipakai sebagai referensi pola
    df_ref = df_real[
        (df_real['partisipasi_politik'] <= 100.0) & 
        (df_real['pengguna_hak_pilih'] <= df_real['dpt'])
    ].copy()
    
    print("--- MEMUAT MODEL OPTIMAL ---")
    model_path = ROOT_DIR / "models" / "random_forest_partisipasi.joblib"
    if not model_path.exists():
        raise FileNotFoundError(f"Model tidak ditemukan di {model_path}. Silakan jalankan scripts/train_model.py terlebih dahulu.")
        
    pipeline = joblib.load(model_path)
    
    print(f"--- GENERASI {num_samples} DATA SINTETIS REALISTIS ---")
    np.random.seed(42)
    
    # Langkah A: Sampling baris referensi (bootstrap) untuk mempertahankan proporsi kategori & hubungan konstan kecamatan
    sampled_indices = np.random.choice(df_ref.index, size=num_samples, replace=True)
    df_synth = df_ref.loc[sampled_indices].copy().reset_index(drop=True)
    
    # Langkah B: Berikan sedikit derau (noise) pada fitur kontinu agar tidak hanya menduplikasi baris
    # Perturbasi DPT
    dpt_noise = np.random.randint(-15, 15, size=num_samples)
    df_synth['dpt'] = (df_synth['dpt'] + dpt_noise).clip(df_ref['dpt'].min(), df_ref['dpt'].max())
    
    # Perturbasi rasio DPT terhadap penduduk kelurahan
    rasio_noise = np.random.normal(0, 0.05 * df_ref['rasio_dpt_terhadap_penduduk_kelurahan'].std(), size=num_samples)
    df_synth['rasio_dpt_terhadap_penduduk_kelurahan'] = (df_synth['rasio_dpt_terhadap_penduduk_kelurahan'] + rasio_noise).clip(0.01, 10.0)
    
    # Catatan: Fitur konstan per kecamatan seperti kepadatan_penduduk dan usia tetap dipertahaman persis
    # seperti baris referensinya agar relasi kecamatan-kepadatan tidak rusak.
    
    # Langkah C: Gunakan model optimal untuk memprediksi partisipasi politik
    # Gunakan nama fitur yang tepat sesuai dengan saat fitting model
    if hasattr(pipeline, 'feature_names_in_'):
        cols_model = list(pipeline.feature_names_in_)
    else:
        # Fallback jika model tidak menyimpan nama fitur
        cols_model = ['dpt', 'rasio_dpt_terhadap_penduduk_kelurahan', 'pendapatan_per_kapita',
                      'tingkat_pengangguran', 'kepadatan_penduduk', 'ipm',
                      'persen_usia_17_24_kec', 'persen_usia_25_44_kec', 'persen_usia_45_plus_kec',
                      'kecamatan', 'kelurahan', 'no_tps']
                      
    X_synth = df_synth[cols_model]
    
    # Prediksi baseline partisipasi
    pred_partisipasi = pipeline.predict(X_synth)
    
    # Langkah D: Tambahkan residual noise agar sebaran target realistis (tidak terlalu sempurna)
    # Gunakan standar deviasi error model pada data latih (sekitar 3.12)
    residual_std = 3.12
    synth_noise = np.random.normal(0, residual_std, size=num_samples)
    target_partisipasi = (pred_partisipasi + synth_noise).clip(0.0, 100.0)
    
    # Langkah E: Sinkronisasikan angka pengguna_hak_pilih dengan DPT dan partisipasi secara logis
    # pengguna_hak_pilih = dpt * (partisipasi_politik / 100)
    pengguna_hak_pilih = np.round(df_synth['dpt'] * (target_partisipasi / 100.0)).astype(int)
    
    # Pastikan pengguna_hak_pilih tidak melebihi DPT
    pengguna_hak_pilih = np.clip(pengguna_hak_pilih, 0, df_synth['dpt'])
    
    # Hitung ulang partisipasi agar 100% konsisten dengan rasio (pengguna_hak_pilih / dpt)
    partisipasi_final = (pengguna_hak_pilih / df_synth['dpt']) * 100.0
    
    df_synth['pengguna_hak_pilih'] = pengguna_hak_pilih
    df_synth['partisipasi_politik'] = partisipasi_final
    df_synth['level_data'] = 'tps_sintetis'  # Beri penanda yang jelas!
    
    # Set ID record agar unik untuk data sintetis
    df_synth['id_record'] = [f"SYNTH-2024-{row['kecamatan']}-{row['kelurahan']}-{idx}" 
                             for idx, row in df_synth.iterrows()]
    
    # Langkah F: Simpan ke database
    print("--- MENYIMPAN DATA SINTETIS KE DATABASE ---")
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # Bersihkan data sintetis sebelumnya jika ada
        cursor.execute("DELETE FROM data_partisipasi_tps WHERE level_data = 'tps_sintetis'")
        print("Data sintetis lama berhasil dibersihkan.")
        
        # Insert data sintetis baru
        success_count = 0
        for _, row in df_synth.iterrows():
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
                int(row['tahun_pemilu']),
                row['level_data'],
                row['kecamatan'],
                row['kelurahan'],
                str(row['no_tps']),
                row['id_record'],
                int(row['dpt']),
                int(row['pengguna_hak_pilih']),
                float(row['partisipasi_politik']),
                int(row['dpt_total_tps']) if pd.notna(row['dpt_total_tps']) else None,
                str(row['penduduk_total_kelurahan']) if pd.notna(row['penduduk_total_kelurahan']) else None,
                int(row['penduduk_total_kecamatan']) if pd.notna(row['penduduk_total_kecamatan']) else None,
                float(row['rasio_dpt_terhadap_penduduk_kelurahan']),
                float(row['pendapatan_per_kapita']),
                float(row['tingkat_pengangguran']),
                float(row['kepadatan_penduduk']),
                float(row['ipm']),
                int(row['jumlah_usia_17_24_kec']) if pd.notna(row['jumlah_usia_17_24_kec']) else None,
                int(row['jumlah_usia_25_44_kec']) if pd.notna(row['jumlah_usia_25_44_kec']) else None,
                int(row['jumlah_usia_45_plus_kec']) if pd.notna(row['jumlah_usia_45_plus_kec']) else None,
                float(row['persen_usia_17_24_kec']),
                float(row['persen_usia_25_44_kec']),
                float(row['persen_usia_45_plus_kec'])
            ))
            success_count += 1
            
        conn.commit()
        
    print(f"Data sintetis sukses digenerasi dan disimpan ke DB: {success_count} baris.")

if __name__ == "__main__":
    generate_synthetic_data()
