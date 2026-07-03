import pandas as pd

from src.config import DISPLAY_NAMES, TARGET_COLUMN


def format_percent(value: float) -> str:
    return f"{value:.2f}%"


def format_rupiah(value: float) -> str:
    return "Rp{:,.0f}".format(value).replace(",", ".")


def rename_for_display(df: pd.DataFrame) -> pd.DataFrame:
    return df.rename(columns=DISPLAY_NAMES)


def get_summary(df: pd.DataFrame) -> dict:
    average = float(df[TARGET_COLUMN].mean())
    highest_row = df.loc[df[TARGET_COLUMN].idxmax()]
    lowest_row = df.loc[df[TARGET_COLUMN].idxmin()]
    return {
        "rows": len(df),
        "average": average,
        "highest_area": highest_row["kecamatan"],
        "highest_value": float(highest_row[TARGET_COLUMN]),
        "lowest_area": lowest_row["kecamatan"],
        "lowest_value": float(lowest_row[TARGET_COLUMN]),
    }
