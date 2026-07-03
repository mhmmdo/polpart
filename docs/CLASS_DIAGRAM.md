# Class Diagram Konseptual Sistem

Class diagram konseptual menggambarkan struktur internal kelas atau modul program Python yang menyusun sistem beserta relasi antar-kelas tersebut.

---

## 1. Class Diagram (Mermaid)

```mermaid
classDiagram
    class Database {
        +db_path : Path
        +get_connection() Connection
        +init_database() void
        +seed_kecamatan() void
    }

    class DataLoader {
        +required_columns : List
        +load_dataset() DataFrame
        +validate_dataset() List
    }

    class Kecamatan {
        +id_kecamatan : int
        +nama_kecamatan : String
    }

    class DataSosioEkonomi {
        +id_sosio : int
        +id_kecamatan : int
        +tahun : int
        +tingkat_pendidikan : float
        +pendapatan_per_kapita : float
        +tingkat_pengangguran : float
        +kepadatan_penduduk : float
        +ipm : float
    }

    class DataPartisipasiPolitik {
        +id_partisipasi : int
        +id_kecamatan : int
        +tahun : int
        +dpt : int
        +pengguna_hak_pilih : int
        +partisipasi_politik : float
        +sumber_data : String
    }

    class ModelEvaluasi {
        +id_evaluasi : int
        +nama_model : String
        +rmse : float
        +r2_score : float
        +jumlah_data : int
        +tanggal_evaluasi : String
    }

    class RandomForestModel {
        +features : List
        +target : String
        +model : RandomForestRegressor
        +rmse : float
        +r2_score : float
        +train_model(df) ModelResult
        +predict(input_values) float
        +evaluate_model() void
        +get_feature_importance() DataFrame
    }

    class PredictionService {
        +predict_participation(model, input_values) float
        +save_prediction(data) void
    }

    class VisualizationService {
        +show_correlation_chart(df) Figure
        +show_prediction_chart(df) Figure
        +show_feature_importance(importance_df) Figure
        +show_map(df, geojson, year) Figure
    }

    %% Relationships
    Kecamatan "1" --o "*" DataSosioEkonomi : memiliki
    Kecamatan "1" --o "*" DataPartisipasiPolitik : memiliki
    Kecamatan "1" --o "*" PredictionService : memiliki (HasilPrediksi)
    RandomForestModel ..> DataLoader : menggunakan dataset
    VisualizationService ..> DataLoader : menggunakan dataset
```

---

## 2. Deskripsi Kelas
1. **Database**: Kelas penanggung jawab yang mengatur siklus basis data SQLite mulai dari inisialisasi, seeding awal data master, dan penyediaan objek koneksi.
2. **DataLoader**: Kelas pembaca dan pembersih data yang bertanggung jawab menyuplai dataframe masukan untuk analisis dan pemodelan.
3. **Kecamatan, DataSosioEkonomi, DataPartisipasiPolitik, ModelEvaluasi**: Representasi entitas data/model domain dari tabel basis data.
4. **RandomForestModel**: Kelas representasi logis algoritma Random Forest untuk pelatihan model, penghitungan metrik akurasi (RMSE, R²), dan ekstraksi pentingnya fitur (*feature importance*).
5. **PredictionService**: Penghubung antara input antarmuka pengguna dengan model terlatih untuk mengeksekusi prediksi tingkat partisipasi politik dan menyimpan log riwayat ke database.
6. **VisualizationService**: Penyedia grafik plotly dan peta choropleth dari data yang disediakan oleh DataLoader.
