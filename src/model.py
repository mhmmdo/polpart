from dataclasses import dataclass
from typing import Any, Dict
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from sklearn.inspection import permutation_importance

# Algoritma Regresi
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, ExtraTreesRegressor
from sklearn.ensemble import HistGradientBoostingRegressor

from src.config import FEATURE_COLUMNS, MODEL_PARAMS, TARGET_COLUMN


@dataclass
class ModelResult:
    # Kelas penyimpan data (blueprint) untuk menampung seluruh hasil dari model setelah belajar
    model: Any
    rmse: float
    mae: float
    r2: float
    feature_importance: pd.DataFrame
    prediction_result: pd.DataFrame
    train_size: int
    test_size: int
    algorithm_comparison: pd.DataFrame = None
    baseline_metrics: Dict[str, float] = None
    best_params: Dict[str, Any] = None


class PoliticalFeatureEngineer(BaseEstimator, TransformerMixin):
    """Custom transformer untuk menghitung deviasi DPT dan jumlah TPS di kelurahan tanpa kebocoran data."""
    def __init__(self):
        self.kelurahan_mean_dpt_ = {}
        self.kelurahan_tps_count_ = {}
        self.global_mean_dpt_ = 0.0
        
    def fit(self, X, y=None):
        if 'kelurahan' in X.columns and 'dpt' in X.columns:
            self.kelurahan_mean_dpt_ = X.groupby('kelurahan')['dpt'].mean().to_dict()
        if 'kelurahan' in X.columns and 'no_tps' in X.columns:
            self.kelurahan_tps_count_ = X.groupby('kelurahan')['no_tps'].nunique().to_dict()
        if 'dpt' in X.columns:
            self.global_mean_dpt_ = X['dpt'].mean()
        else:
            self.global_mean_dpt_ = 0.0
        return self
        
    def transform(self, X):
        X_out = X.copy()
        if 'kelurahan' in X_out.columns and 'dpt' in X_out.columns:
            mean_dpt = X_out['kelurahan'].map(self.kelurahan_mean_dpt_).fillna(self.global_mean_dpt_)
            X_out['dpt_dev_kelurahan'] = X_out['dpt'] - mean_dpt
        else:
            X_out['dpt_dev_kelurahan'] = 0.0
            
        if 'kelurahan' in X_out.columns:
            X_out['tps_count_kelurahan'] = X_out['kelurahan'].map(self.kelurahan_tps_count_).fillna(1)
        else:
            X_out['tps_count_kelurahan'] = 1.0
            
        return X_out


def train_random_forest(df: pd.DataFrame) -> ModelResult:
    """Fungsi utama untuk melatih, mengevaluasi, membandingkan, dan mengoptimalkan model regresi."""
    
    # 1. EVALUASI MODEL BASELINE (SEBELUM OPTIMASI)
    # Model baseline melatih RandomForestRegressor menggunakan data mentah dan tanpa fitur kategorikal/rekayasa.
    df_baseline = df.dropna(subset=[*FEATURE_COLUMNS, TARGET_COLUMN]).copy()
    
    if len(df_baseline) < 8:
        raise ValueError("Data terlalu sedikit untuk evaluasi model baseline.")
        
    x_base = df_baseline[FEATURE_COLUMNS]
    y_base = df_baseline[TARGET_COLUMN]
    
    test_size = 0.25 if len(df_baseline) >= 12 else 0.3
    x_train_base, x_test_base, y_train_base, y_test_base = train_test_split(
        x_base, y_base, test_size=test_size, random_state=42
    )
    
    model_base = RandomForestRegressor(**MODEL_PARAMS)
    model_base.fit(x_train_base, y_train_base)
    y_pred_base = model_base.predict(x_test_base)
    
    baseline_metrics = {
        "r2": float(r2_score(y_test_base, y_pred_base)) if len(y_test_base) > 1 else 0.0,
        "mae": float(mean_absolute_error(y_test_base, y_pred_base)),
        "rmse": float(np.sqrt(mean_squared_error(y_test_base, y_pred_base)))
    }

    # 2. PEMBERSIHAN DATA (MENGHAPUS ANOMALI)
    # Menghapus data jika partisipasi > 100% atau pengguna_hak_pilih > dpt
    df_clean = df.dropna(subset=[*FEATURE_COLUMNS, TARGET_COLUMN, 'kecamatan', 'kelurahan']).copy()
    df_clean = df_clean[
        (df_clean[TARGET_COLUMN] <= 100.0) & 
        (df_clean['pengguna_hak_pilih'] <= df_clean['dpt'])
    ].copy()

    if len(df_clean) < 8:
        raise ValueError("Data setelah pembersihan terlalu sedikit untuk melanjutkan modeling.")

    # 3. MENYIAPKAN FITUR & TARGET BARU
    # Tentukan nama kolom tahun jika ada
    year_col = 'tahun' if 'tahun' in df_clean.columns else ('tahun_pemilu' if 'tahun_pemilu' in df_clean.columns else None)

    # Kita menggunakan fitur asli + kecamatan + kelurahan + no_tps (no_tps digunakan oleh transformer)
    cols_to_use = list(FEATURE_COLUMNS) + ['kecamatan', 'kelurahan', 'no_tps']
    if year_col:
        cols_to_use.append(year_col)
    cols_to_use = list(dict.fromkeys(cols_to_use))  # Hapus duplikat nama kolom
    
    # Abaikan kolom konstan dari pencantuman di preprocessor, tapi tetap masukkan kolom lain
    non_constant_numeric = [
        'dpt', 'rasio_dpt_terhadap_penduduk_kelurahan', 'kepadatan_penduduk',
        'persen_usia_17_24_kec', 'persen_usia_25_44_kec', 'persen_usia_45_plus_kec',
        'dpt_dev_kelurahan', 'tps_count_kelurahan'
    ]
    if year_col:
        non_constant_numeric.append(year_col)

    x = df_clean[cols_to_use]
    y = df_clean[TARGET_COLUMN]

    # 4. MEMBAGI DATA DENGAN PREVENTIF DATA LEAKAGE
    x_train, x_test, y_train, y_test = train_test_split(
        x, y, test_size=test_size, random_state=42
    )

    # 5. MENENTUKAN PIPELINE PREPROCESSING
    preprocessor = ColumnTransformer(
        transformers=[
            ('cat', OneHotEncoder(handle_unknown='ignore', sparse_output=False), ['kecamatan', 'kelurahan']),
            ('num', StandardScaler(), non_constant_numeric)
        ],
        remainder='drop'
    )

    # 6. KOMPARASI BEBERAPA ALGORITMA
    algorithms = {
        "Linear Regression": LinearRegression(),
        "Ridge Regression": Ridge(alpha=1.0),
        "Random Forest": RandomForestRegressor(n_estimators=100, random_state=42, max_depth=10),
        "Gradient Boosting": GradientBoostingRegressor(n_estimators=100, random_state=42, max_depth=4),
        "Hist Gradient Boosting": HistGradientBoostingRegressor(random_state=42, max_depth=5),
        "Extra Trees": ExtraTreesRegressor(n_estimators=100, random_state=42, max_depth=10)
    }

    comp_list = []
    trained_pipelines = {}

    for name, model_obj in algorithms.items():
        pipeline = Pipeline([
            ('engineer', PoliticalFeatureEngineer()),
            ('preprocessor', preprocessor),
            ('model', model_obj)
        ])
        pipeline.fit(x_train, y_train)
        y_pred = pipeline.predict(x_test)
        
        r2 = float(r2_score(y_test, y_pred)) if len(y_test) > 1 else 0.0
        mae = float(mean_absolute_error(y_test, y_pred))
        rmse = float(np.sqrt(mean_squared_error(y_test, y_pred)))
        
        comp_list.append({
            "Algoritma": name,
            "R2 Score": r2,
            "MAE": mae,
            "RMSE": rmse
        })
        trained_pipelines[name] = pipeline

    algorithm_comparison = pd.DataFrame(comp_list).sort_values("R2 Score", ascending=False)
    
    # 7. PILIH ALGORITMA TERBAIK & HYPERPARAMETER TUNING
    best_algo_name = algorithm_comparison.iloc[0]["Algoritma"]
    
    # Buat pipeline baru untuk tuning agar GridSearchCV berjalan dari data mentah (menghindari leakage)
    if best_algo_name == "Hist Gradient Boosting":
        tuning_pipeline = Pipeline([
            ('engineer', PoliticalFeatureEngineer()),
            ('preprocessor', preprocessor),
            ('model', HistGradientBoostingRegressor(random_state=42))
        ])
        param_grid = {
            'model__max_iter': [50, 100, 150],
            'model__max_depth': [3, 5, 7],
            'model__learning_rate': [0.05, 0.1, 0.2],
            'model__min_samples_leaf': [5, 10, 20]
        }
    else:
        # Fallback ke Random Forest tuning
        tuning_pipeline = Pipeline([
            ('engineer', PoliticalFeatureEngineer()),
            ('preprocessor', preprocessor),
            ('model', RandomForestRegressor(random_state=42))
        ])
        param_grid = {
            'model__n_estimators': [100, 200, 300],
            'model__max_depth': [6, 10, 15],
            'model__min_samples_leaf': [1, 2, 4]
        }

    grid = GridSearchCV(tuning_pipeline, param_grid, cv=5, scoring='r2', n_jobs=-1)
    grid.fit(x_train, y_train)
    
    best_pipeline = grid.best_estimator_
    best_params = grid.best_params_
    
    # 8. EVALUASI AKHIR MODEL TERBAIK YANG TELAH DITUNING
    y_pred_final = best_pipeline.predict(x_test)
    rmse_final = float(np.sqrt(mean_squared_error(y_test, y_pred_final)))
    mae_final = float(mean_absolute_error(y_test, y_pred_final))
    r2_final = float(r2_score(y_test, y_pred_final)) if len(y_test) > 1 else 0.0

    # 9. PERMUTATION IMPORTANCE (UNTUK FITUR UTAMA DI TINGKAT VARIABEL INPUT)
    r_importance = permutation_importance(best_pipeline, x_test, y_test, n_repeats=5, random_state=42)
    importance = pd.DataFrame(
        {
            "variabel": x_test.columns.tolist(),
            "importance": r_importance.importances_mean,
        }
    ).sort_values("importance", ascending=False)

    # 10. MENYUSUN HASIL PREDIKSI (SAMPEL DATA UJI)
    prediction_result = pd.DataFrame(
        {
            "aktual": y_test.to_numpy(),
            "prediksi": y_pred_final,
            "selisih": y_test.to_numpy() - y_pred_final,
        }
    )

    # 11. MENYIMPAN HASIL KE DATABASE
    try:
        from src.database import save_model_evaluation
        save_model_evaluation({
            "nama_model": f"Tuned {best_algo_name}",
            "rmse": rmse_final,
            "mae": mae_final,
            "r2_score": r2_final,
            "jumlah_data": len(df_clean),
            "jumlah_training": len(x_train),
            "jumlah_testing": len(x_test)
        })
    except Exception as e:
        import sys
        print(f"Warning: Gagal menyimpan evaluasi model ke database: {e}", file=sys.stderr)

    return ModelResult(
        model=best_pipeline,
        rmse=rmse_final,
        mae=mae_final,
        r2=r2_final,
        feature_importance=importance,
        prediction_result=prediction_result,
        train_size=len(x_train),
        test_size=len(x_test),
        algorithm_comparison=algorithm_comparison,
        baseline_metrics=baseline_metrics,
        best_params=best_params
    )


def predict_participation(model: Any, input_values: dict) -> float:
    """Fungsi pembantu: Digunakan oleh halaman Prediksi untuk menebak nilai secara instan"""
    row = pd.DataFrame([input_values])
    pred = float(model.predict(row)[0])
    return min(max(pred, 0.0), 100.0) # Batasi hasil prediksi agar rasional antara 0% s.d 100%

