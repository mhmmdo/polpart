import streamlit as st
from pathlib import Path
from src.config import STYLE_PATH
from streamlit_option_menu import option_menu

# Mengatur konfigurasi halaman secara global (Hanya boleh dipanggil sekali di file utama ini!)
# page_title: Judul yang muncul di tab browser
# layout="wide": Menggunakan lebar layar penuh
# initial_sidebar_state="expanded": Membiarkan menu samping (sidebar) terbuka sejak awal
st.set_page_config(
    page_title="Sistem Prediksi Partisipasi Politik",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Memasukkan kode CSS kustom untuk mempercantik tampilan agar lebih rapi
if STYLE_PATH.exists():
    st.markdown(f"<style>{STYLE_PATH.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)

# Mendefinisikan halaman-halaman yang ada di sistem (menghubungkan file dengan nama halamannya)
dashboard = st.Page("pages/1_Dashboard.py", title="Dashboard", default=True)
data_historis = st.Page("pages/2_Data_Historis.py", title="Data Historis")
prediksi = st.Page("pages/3_Prediksi.py", title="Prediksi RF")
visualisasi = st.Page("pages/4_Visualisasi.py", title="Visualisasi & Peta")
tentang = st.Page("pages/5_Tentang.py", title="Tentang Aplikasi")

# Membuat menu navigasi kustom menggunakan library streamlit-option-menu
page_names = ["Dashboard", "Data Historis", "Prediksi", "Visualisasi", "Tentang"]
page_files = [
    "pages/1_Dashboard.py",
    "pages/2_Data_Historis.py",
    "pages/3_Prediksi.py",
    "pages/4_Visualisasi.py",
    "pages/5_Tentang.py"
]

# Mengambil status halaman yang sedang aktif saat ini dari memory (session_state)
current_page = st.session_state.get("current_page", "Dashboard")
try:
    default_index = page_names.index(current_page)
except ValueError:
    default_index = 0

# Menggambar menu sidebar di sebelah kiri layar
with st.sidebar:
    selected = option_menu(
        "PolPart RF", # Judul Aplikasi di menu
        options=page_names, # Pilihan menunya
        icons=["grid-fill", "table", "cpu", "map-fill", "info-circle-fill"], # Icon masing-masing menu
        menu_icon="activity",
        default_index=default_index,
        styles={
            # Konfigurasi warna, jenis font, dan ukuran menu sidebar
            "container": {"background-color": "#ffffff", "padding": "5px 0px"},
            "icon": {"color": "#475569", "font-size": "15px"},
            "menu-title": {"color": "#1E293B", "font-family": "Plus Jakarta Sans", "font-weight": "800"},
            "nav-link": {
                "color": "#475569",
                "font-family": "Plus Jakarta Sans",
                "font-weight": "600",
                "font-size": "13px",
                "text-align": "left",
                "margin": "0px",
            },
            "nav-link-selected": {"background-color": "#ff7f66", "color": "#FFFFFF"}, # Warna menu saat dipilih (orange)
        }
    )

# Jika pengguna mengklik menu lain, pindahkan halamannya (switch_page)
if selected != current_page:
    st.session_state["current_page"] = selected
    st.switch_page(page_files[page_names.index(selected)])

# Membuat navigasi bawaan streamlit dan menjalankannya secara tersembunyi
# position="hidden" digunakan agar menu default Streamlit tidak muncul (tidak dobel dengan menu kustom kita)
pg = st.navigation([dashboard, data_historis, prediksi, visualisasi, tentang], position="hidden")
pg.run()
