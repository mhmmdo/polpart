"""
Script untuk melatih (training) model Machine Learning (Random Forest) 
menggunakan dataset partisipasi politik dan menyimpan model yang sudah dilatih.
"""
from pathlib import Path
import sys

import joblib

# Menambahkan root folder project ke dalam path agar bisa import dari folder src
ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_DIR))

from src.config import MODEL_DIR
from src.data_loader import load_dataset
from src.model import train_random_forest


def main():
    """Fungsi utama untuk melatih model dan menyimpannya ke dalam file."""
    # Memuat dataset
    df = load_dataset()
    result = train_random_forest(df)

    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    model_path = MODEL_DIR / "random_forest_partisipasi.joblib"
    joblib.dump(result.model, model_path)

    print("Model berhasil disimpan:", model_path)
    print("\n--- METRIK SEBELUM OPTIMASI (BASELINE) ---")
    if result.baseline_metrics:
        print(f"R2 Score : {result.baseline_metrics['r2']:.4f}")
        print(f"MAE      : {result.baseline_metrics['mae']:.4f}")
        print(f"RMSE     : {result.baseline_metrics['rmse']:.4f}")
        
    print("\n--- METRIK SESUDAH OPTIMASI (TUNED MODEL) ---")
    print(f"R2 Score : {result.r2:.4f}")
    print(f"MAE      : {result.mae:.4f}")
    print(f"RMSE     : {result.rmse:.4f}")
    print(f"Best Hyperparameters: {result.best_params}")


if __name__ == "__main__":
    main()
