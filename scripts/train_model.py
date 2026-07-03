from pathlib import Path
import sys

import joblib

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_DIR))

from src.config import MODEL_DIR
from src.data_loader import load_dataset
from src.model import train_random_forest


def main():
    df = load_dataset()
    result = train_random_forest(df)

    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    model_path = MODEL_DIR / "random_forest_partisipasi.joblib"
    joblib.dump(result.model, model_path)

    print("Model berhasil disimpan:", model_path)
    print(f"RMSE: {result.rmse:.3f}")
    print(f"R2  : {result.r2:.3f}")


if __name__ == "__main__":
    main()
