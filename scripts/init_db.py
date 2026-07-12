"""
Script untuk menginisialisasi database SQLite dan membuat skema tabel.
Juga melakukan seeding (pengisian awal) data kecamatan jika diperlukan.
"""
from pathlib import Path
import sys

# Menambahkan root folder project ke dalam system path agar modul 'src' bisa di-import
ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_DIR))

from src.database import init_database, seed_kecamatan, seed_admin, seed_dapil, seed_partai, seed_pemilu
from src.config import DB_PATH

def main():
    """Fungsi utama untuk menjalankan proses inisialisasi database."""
    print("Inisialisasi database...")
    try:
        if DB_PATH.exists():
            print(f"Menghapus database lama di {DB_PATH}...")
            try:
                DB_PATH.unlink()
            except Exception as unlink_err:
                print(f"Peringatan: Gagal menghapus database lama: {unlink_err}")
                
        init_database()
        print("Skema database berhasil diterapkan.")

        seed_kecamatan()
        print("Seeding data kecamatan default selesai.")

        seed_dapil()
        print("Seeding data dapil selesai.")

        seed_partai()
        print("Seeding data partai politik selesai.")

        seed_pemilu()
        print("Seeding data pemilu selesai.")

        seed_admin()
        print("Seeding akun Admin/User default selesai.")
        
        print("Mengimpor data TPS dari CSV...")
        from scripts.import_tps_csv import main as import_tps_data
        import_tps_data()
        
        print("Database berhasil dibuat di:", DB_PATH)
        print("Inisialisasi selesai dengan sukses!")
    except Exception as e:
        print(f"Error saat inisialisasi database: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
