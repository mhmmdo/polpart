from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
RAW_DATA_PATH = DATA_DIR / "raw" / "data_partisipasi_politik_sample.csv"
GEOJSON_PATH = DATA_DIR / "geo" / "kecamatan_5.geojson"
MODEL_DIR = BASE_DIR / "models"
DB_PATH = BASE_DIR / "database" / "polpart.db"
ASSETS_DIR = BASE_DIR / "assets"
STYLE_PATH = ASSETS_DIR / "style.css"

APP_TITLE = "Prediksi Partisipasi Politik"
APP_SUBTITLE = "Dashboard dan prediksi tingkat partisipasi politik berbasis Random Forest"

TARGET_COLUMN = "partisipasi_politik"
YEAR_COLUMN = "tahun"
AREA_COLUMN = "kecamatan"

FEATURE_COLUMNS = [
    "tingkat_pendidikan",
    "pendapatan_per_kapita",
    "tingkat_pengangguran",
    "kepadatan_penduduk",
    "ipm",
]

REQUIRED_COLUMNS = [YEAR_COLUMN, AREA_COLUMN, *FEATURE_COLUMNS, TARGET_COLUMN]

DISPLAY_NAMES = {
    "tahun": "Tahun",
    "kecamatan": "Kecamatan",
    "tingkat_pendidikan": "Tingkat Pendidikan (%)",
    "pendapatan_per_kapita": "Pendapatan per Kapita (Rp)",
    "tingkat_pengangguran": "Tingkat Pengangguran (%)",
    "kepadatan_penduduk": "Kepadatan Penduduk",
    "ipm": "IPM",
    "partisipasi_politik": "Partisipasi Politik (%)",
}

MODEL_PARAMS = {
    "n_estimators": 300,
    "max_depth": 8,
    "random_state": 42,
    "min_samples_leaf": 1,
}
