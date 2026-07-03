from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import train_test_split

from src.config import FEATURE_COLUMNS, MODEL_PARAMS, TARGET_COLUMN


@dataclass
class ModelResult:
    model: RandomForestRegressor
    rmse: float
    r2: float
    feature_importance: pd.DataFrame
    prediction_result: pd.DataFrame
    train_size: int
    test_size: int


def train_random_forest(df: pd.DataFrame) -> ModelResult:
    """Train Random Forest Regression for political participation prediction."""
    data = df.dropna(subset=[*FEATURE_COLUMNS, TARGET_COLUMN]).copy()

    if len(data) < 8:
        raise ValueError("Data terlalu sedikit. Diperlukan minimal 8 baris data untuk evaluasi model yang valid.")

    x = data[FEATURE_COLUMNS]
    y = data[TARGET_COLUMN]

    test_size = 0.25 if len(data) >= 12 else 0.3
    x_train, x_test, y_train, y_test = train_test_split(
        x,
        y,
        test_size=test_size,
        random_state=42,
    )

    model = RandomForestRegressor(**MODEL_PARAMS)
    model.fit(x_train, y_train)

    y_pred = model.predict(x_test)
    rmse = float(np.sqrt(mean_squared_error(y_test, y_pred)))
    r2 = float(r2_score(y_test, y_pred)) if len(y_test) > 1 else 0.0

    importance = pd.DataFrame(
        {
            "variabel": FEATURE_COLUMNS,
            "importance": model.feature_importances_,
        }
    ).sort_values("importance", ascending=False)

    prediction_result = pd.DataFrame(
        {
            "aktual": y_test.to_numpy(),
            "prediksi": y_pred,
            "selisih": y_test.to_numpy() - y_pred,
        }
    )

    # Save model evaluation to database
    try:
        from src.database import save_model_evaluation
        save_model_evaluation({
            "nama_model": "Random Forest",
            "rmse": rmse,
            "r2_score": r2,
            "jumlah_data": len(data),
            "jumlah_training": len(x_train),
            "jumlah_testing": len(x_test)
        })
    except Exception as e:
        # Avoid crashing if DB fails, print warning
        import sys
        print(f"Warning: Gagal menyimpan evaluasi model ke database: {e}", file=sys.stderr)

    return ModelResult(
        model=model,
        rmse=rmse,
        r2=r2,
        feature_importance=importance,
        prediction_result=prediction_result,
        train_size=len(x_train),
        test_size=len(x_test),
    )


def predict_participation(model: RandomForestRegressor, input_values: dict) -> float:
    row = pd.DataFrame([input_values], columns=FEATURE_COLUMNS)
    return float(model.predict(row)[0])
