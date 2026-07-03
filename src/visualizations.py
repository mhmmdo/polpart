import pandas as pd
import plotly.express as px

from src.config import AREA_COLUMN, DISPLAY_NAMES, FEATURE_COLUMNS, TARGET_COLUMN, YEAR_COLUMN


def participation_by_area(df: pd.DataFrame):
    chart_data = (
        df.groupby(AREA_COLUMN, as_index=False)[TARGET_COLUMN]
        .mean()
        .sort_values(TARGET_COLUMN, ascending=False)
    )
    fig = px.bar(
        chart_data,
        x=AREA_COLUMN,
        y=TARGET_COLUMN,
        text=TARGET_COLUMN,
        labels=DISPLAY_NAMES,
        title="Rata-rata Partisipasi Politik per Kecamatan",
        template="plotly_white",
        color_discrete_sequence=["#2563EB"],
    )
    fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
    fig.update_layout(yaxis_ticksuffix="%", xaxis_title="", yaxis_title="Partisipasi Politik")
    return fig


def participation_trend(df: pd.DataFrame):
    chart_data = df.sort_values([AREA_COLUMN, YEAR_COLUMN])
    fig = px.line(
        chart_data,
        x=YEAR_COLUMN,
        y=TARGET_COLUMN,
        color=AREA_COLUMN,
        markers=True,
        labels=DISPLAY_NAMES,
        title="Tren Partisipasi Politik per Tahun",
        template="plotly_white",
        color_discrete_sequence=px.colors.qualitative.Safe,
    )
    fig.update_layout(yaxis_ticksuffix="%", xaxis_title="Tahun", yaxis_title="Partisipasi Politik")
    return fig


def correlation_heatmap(df: pd.DataFrame):
    corr_cols = [*FEATURE_COLUMNS, TARGET_COLUMN]
    corr = df[corr_cols].corr(numeric_only=True)
    fig = px.imshow(
        corr,
        text_auto=".2f",
        aspect="auto",
        title="Korelasi Antar Variabel",
        labels={"color": "Korelasi"},
        template="plotly_white",
        color_continuous_scale="Blues",
    )
    return fig


def feature_importance_bar(importance_df: pd.DataFrame):
    fig = px.bar(
        importance_df,
        x="importance",
        y="variabel",
        orientation="h",
        text="importance",
        title="Feature Importance Random Forest",
        template="plotly_white",
        color_discrete_sequence=["#2563EB"],
    )
    fig.update_traces(texttemplate="%{text:.3f}", textposition="outside")
    fig.update_layout(yaxis={"categoryorder": "total ascending"}, xaxis_title="Importance", yaxis_title="")
    return fig


def prediction_scatter(prediction_df: pd.DataFrame):
    fig = px.scatter(
        prediction_df,
        x="aktual",
        y="prediksi",
        size=prediction_df["selisih"].abs() + 1,
        title="Perbandingan Nilai Aktual vs Prediksi",
        labels={"aktual": "Aktual", "prediksi": "Prediksi"},
        template="plotly_white",
        color_discrete_sequence=["#2563EB"],
    )
    min_value = min(prediction_df["aktual"].min(), prediction_df["prediksi"].min())
    max_value = max(prediction_df["aktual"].max(), prediction_df["prediksi"].max())
    fig.add_shape(
        type="line",
        x0=min_value,
        y0=min_value,
        x1=max_value,
        y1=max_value,
        line={"dash": "dash", "color": "#64748B"},
    )
    return fig


def participation_map(df: pd.DataFrame, geojson: dict, selected_year: int):
    map_data = df[df[YEAR_COLUMN] == selected_year].copy()
    if map_data.empty:
        map_data = df.groupby(AREA_COLUMN, as_index=False)[TARGET_COLUMN].mean()

    fig = px.choropleth_mapbox(
        map_data,
        geojson=geojson,
        locations=AREA_COLUMN,
        featureidkey="properties.WADMKC",
        color=TARGET_COLUMN,
        hover_name=AREA_COLUMN,
        hover_data={TARGET_COLUMN: ":.2f"},
        center={"lat": -3.335, "lon": 114.59},
        zoom=10.5,
        mapbox_style="carto-positron",
        opacity=0.65,
        labels=DISPLAY_NAMES,
        title=f"Peta Partisipasi Politik Tahun {selected_year}",
    )
    fig.update_layout(margin={"r": 0, "t": 50, "l": 0, "b": 0})
    return fig
