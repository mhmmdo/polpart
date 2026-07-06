"""
Script untuk menginisialisasi database SQLite dan membuat skema tabel.
Juga melakukan seeding (pengisian awal) data kecamatan jika diperlukan.
"""
from pathlib import Path
import sys

# Menambahkan root folder project ke dalam system path agar modul 'src' bisa di-import
ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_DIR))

from src.database import init_database, seed_kecamatan
from src.config import DB_PATH

def main():
    """Fungsi utama untuk menjalankan proses inisialisasi database."""
    print("Inisialisasi database...")
    try:
        init_database()
        print("Skema database berhasil diterapkan.")

        seed_kecamatan()
        print("Seeding data kecamatan default selesai.")

        print("Database berhasil dibuat di:", DB_PATH)
        print("Inisialisasi selesai dengan sukses!")
    except Exception as e:
        print(f"Error saat inisialisasi database: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
