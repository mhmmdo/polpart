"""
Modul ini bertanggung jawab untuk memuat dan memproses data awal 
sebelum digunakan oleh aplikasi (seperti membaca data dari database atau membersihkan data).
"""
import json
from pathlib import Path
from typing import Iterable

import pandas as pd
import streamlit as st

from src.config import GEOJSON_PATH, RAW_DATA_PATH, REQUIRED_COLUMNS


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize column names so CSV from Excel does not explode instantly."""
    clean = df.copy()
    clean.columns = (
        clean.columns.astype(str)
        .str.strip()
        .str.lower()
        .str.replace(" ", "_", regex=False)
        .str.replace("-", "_", regex=False)
    )
    return clean


def validate_columns(df: pd.DataFrame, required_columns: Iterable[str] = REQUIRED_COLUMNS) -> list[str]:
    return [col for col in required_columns if col not in df.columns]


def coerce_numeric_columns(df: pd.DataFrame) -> pd.DataFrame:
    clean = df.copy()
    for column in clean.columns:
        if column not in ["kecamatan", "kelurahan", "no_tps", "id_record", "jenis_kelamin", "penduduk_total_kelurahan"]:
            clean[column] = pd.to_numeric(clean[column], errors="coerce")
    return clean


def load_dataset() -> pd.DataFrame:
    from src.database import get_dataset_final, database_exists
    if not database_exists():
        return pd.DataFrame()
    try:
        return get_dataset_final()
    except Exception:
        return pd.DataFrame()


def get_training_dataset() -> pd.DataFrame:
    """Retrieves dataset_final and drops rows with missing target or features."""
    df = load_dataset()
    if df.empty:
        return pd.DataFrame()
    cols = [
        "dpt",
        "rasio_dpt_terhadap_penduduk_kelurahan",
        "persen_usia_17_24_kec",
        "persen_usia_25_44_kec",
        "persen_usia_45_plus_kec",
        "partisipasi_politik"
    ]
    return df.dropna(subset=cols).reset_index(drop=True)


@st.cache_data(show_spinner=False)
def load_geojson(path: str | Path = GEOJSON_PATH) -> dict:
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def filter_dataset(df: pd.DataFrame, selected_years: list[int], selected_areas: list[str]) -> pd.DataFrame:
    filtered = df.copy()
    if selected_years:
        filtered = filtered[filtered["tahun"].isin(selected_years)]
    if selected_areas:
        filtered = filtered[filtered["kecamatan"].isin(selected_areas)]
    return filtered.reset_index(drop=True)
