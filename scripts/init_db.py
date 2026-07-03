from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_DIR))

from src.database import init_database, seed_kecamatan, seed_admin
from src.config import DB_PATH

def main():
    print("Inisialisasi database...")
    try:
        # Run DB initialization and seeding
        init_database()
        print("Skema database berhasil diterapkan.")
        
        seed_kecamatan()
        print("Seeding data kecamatan default selesai.")
        
        seed_admin()
        print("Seeding akun Admin default selesai.")
        
        print("Database berhasil dibuat di:", DB_PATH)
        print("Inisialisasi selesai dengan sukses!")
    except Exception as e:
        print(f"Error saat inisialisasi database: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
