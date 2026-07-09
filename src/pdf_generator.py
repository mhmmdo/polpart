from fpdf import FPDF
from datetime import datetime
import io

class PolPartPDF(FPDF):
    def header(self):
        # Draw a top coral/mint header banner
        self.set_fill_color(234, 248, 248) # Mint background (#eaf8f8)
        self.rect(0, 0, 210, 20, "F")
        
        self.set_fill_color(255, 127, 102) # Coral strip (#ff7f66)
        self.rect(0, 20, 210, 2, "F")
        
        self.set_y(6)
        self.set_font("helvetica", "B", 12)
        self.set_text_color(30, 41, 59) # Slate Dark (#1e293b)
        self.cell(0, 8, "LAPORAN REKAPITULASI PREDIKSI PARTISIPASI POLITIK", align="C", ln=True)
        self.ln(10)
        
    def footer(self):
        self.set_y(-20)
        self.set_fill_color(241, 245, 249) # Light slate footer
        self.rect(0, 280, 210, 17, "F")
        self.set_y(-15)
        self.set_font("helvetica", "I", 8)
        self.set_text_color(100, 116, 139) # Slate lighter
        self.cell(0, 10, f"Halaman {self.page_no()} | Dokumen hasil analisa otomatis sistem PolPart RF", align="C")

def generate_recap_pdf(data: dict) -> bytes:
    """
    Generates a PDF recap file in-memory and returns the bytes.
    Expects data keys:
      - kecamatan
      - kelurahan
      - no_tps
      - dpt
      - rasio_dpt
      - usia_17_24
      - usia_25_44
      - usia_45_plus
      - hasil_prediksi
      - model_metrics (dict: r2, rmse)
      - printed_by
    """
    pdf = PolPartPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=25)
    pdf.add_page()
    
    # Title
    pdf.set_y(30)
    pdf.set_font("helvetica", "B", 13)
    pdf.set_text_color(255, 127, 102) # Coral
    pdf.cell(0, 10, "REKAP HASIL PREDIKSI (RANDOM FOREST REGRESSOR)", ln=True, align="L")
    
    # Metadata info (2 columns)
    pdf.set_font("helvetica", "", 10)
    pdf.set_text_color(71, 85, 105) # Slate grey
    
    col_width = 90
    current_time = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    
    # Line 1
    pdf.cell(col_width, 6, f"Tanggal Cetak: {current_time}", ln=False)
    pdf.cell(col_width, 6, f"Dicetak Oleh: {data.get('printed_by', 'Guest')}", ln=True)
    
    # Line 2
    pdf.cell(col_width, 6, f"Kecamatan: {data.get('kecamatan', '-')}", ln=False)
    pdf.cell(col_width, 6, f"Kelurahan / Desa: {data.get('kelurahan', '-')}", ln=True)
    
    # Line 3
    pdf.cell(col_width, 6, f"Nomor TPS: {data.get('no_tps', '-')}", ln=False)
    pdf.cell(col_width, 6, "Metode Analisa: Random Forest Regressor", ln=True)
    
    pdf.ln(4)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(4)
    
    # Input Variables Header
    pdf.set_font("helvetica", "B", 11)
    pdf.set_text_color(30, 41, 59)
    pdf.cell(0, 8, "1. Parameter Demografi & Lokasi (Variabel Input)", ln=True)
    pdf.ln(2)
    
    # Table of inputs with soft borders
    pdf.set_draw_color(226, 232, 240) # Soft grey borders
    pdf.set_font("helvetica", "B", 10)
    pdf.set_fill_color(234, 248, 248) # Mint header
    pdf.set_text_color(30, 41, 59)
    
    pdf.cell(100, 8, " Nama Variabel / Parameter", border=1, fill=True, align="L")
    pdf.cell(90, 8, " Nilai Input", border=1, fill=True, align="C", ln=True)
    
    pdf.set_font("helvetica", "", 10)
    
    # Rows
    pdf.cell(100, 8, " Jumlah Daftar Pemilih Tetap (DPT) TPS", border=1, align="L")
    pdf.cell(90, 8, f" {data.get('dpt', 0):,}".replace(",", "."), border=1, align="C", ln=True)
    
    pdf.cell(100, 8, " Rasio DPT Terhadap Penduduk Kelurahan", border=1, align="L")
    pdf.cell(90, 8, f" {data.get('rasio_dpt', 0.0):.4f}", border=1, align="C", ln=True)
    
    pdf.cell(100, 8, " Pendapatan Per Kapita (Rp)", border=1, align="L")
    pdf.cell(90, 8, f" Rp {data.get('pendapatan_per_kapita', 0.0):,}".replace(",", "."), border=1, align="C", ln=True)
    
    pdf.cell(100, 8, " Tingkat Pengangguran Kecamatan (%)", border=1, align="L")
    pdf.cell(90, 8, f" {data.get('tingkat_pengangguran', 0.0):.2f}%", border=1, align="C", ln=True)
    
    pdf.cell(100, 8, " Kepadatan Penduduk (jiwa/km²)", border=1, align="L")
    pdf.cell(90, 8, f" {data.get('kepadatan_penduduk', 0.0):.2f}", border=1, align="C", ln=True)
    
    pdf.cell(100, 8, " Indeks Pembangunan Manusia (IPM)", border=1, align="L")
    pdf.cell(90, 8, f" {data.get('ipm', 0.0):.2f}", border=1, align="C", ln=True)
    
    pdf.cell(100, 8, " Persentase Pemilih Usia 17 - 24 Tahun (Kecamatan)", border=1, align="L")
    pdf.cell(90, 8, f" {data.get('usia_17_24', 0.0):.2f}%", border=1, align="C", ln=True)
    
    pdf.cell(100, 8, " Persentase Pemilih Usia 25 - 44 Tahun (Kecamatan)", border=1, align="L")
    pdf.cell(90, 8, f" {data.get('usia_25_44', 0.0):.2f}%", border=1, align="C", ln=True)
    
    pdf.cell(100, 8, " Persentase Pemilih Usia 45 Tahun Keatas (Kecamatan)", border=1, align="L")
    pdf.cell(90, 8, f" {data.get('usia_45_plus', 0.0):.2f}%", border=1, align="C", ln=True)
    
    pdf.ln(8)
    
    # Prediction Results Box
    pdf.set_fill_color(255, 247, 245) # Light peach card background
    pdf.rect(10, pdf.get_y(), 190, 22, "F")
    
    pdf.set_y(pdf.get_y() + 4)
    pdf.set_font("helvetica", "B", 10)
    pdf.set_text_color(239, 68, 68) # Coral red
    pdf.cell(0, 5, "    OUTPUT PREDIKSI MODEL:", ln=True, align="L")
    
    pdf.set_font("helvetica", "B", 14)
    pdf.set_text_color(255, 127, 102) # Coral accent
    hasil_str = f"{data.get('hasil_prediksi', 0.0):.2f}%"
    pdf.cell(0, 8, f"    Tingkat Partisipasi Politik Prediksi: {hasil_str}", ln=True, align="L")
    
    pdf.ln(10)
    
    # Model evaluation metrics
    pdf.set_font("helvetica", "B", 11)
    pdf.set_text_color(30, 41, 59)
    pdf.cell(0, 8, "2. Performa Model Acuan (Random Forest Regressor)", ln=True)
    pdf.ln(2)
    
    metrics = data.get("model_metrics", {})
    r2 = metrics.get("r2", 0.0)
    rmse = metrics.get("rmse", 0.0)
    mae = metrics.get("mae", 0.0)
    
    # Draw a clean, borderless metric block
    pdf.set_fill_color(248, 250, 252) # Soft light slate background
    pdf.rect(10, pdf.get_y(), 190, 16, "F")
    
    pdf.set_y(pdf.get_y() + 4)
    pdf.set_font("helvetica", "B", 10)
    pdf.set_text_color(71, 85, 105)
    
    pdf.cell(63, 8, f"   R2 Score :  {r2:.4f} ({r2*100:.1f}%)", ln=False)
    pdf.cell(63, 8, f"   RMSE :  {rmse:.4f}", ln=False)
    pdf.cell(64, 8, f"   MAE :  {mae:.4f}", ln=True)
    
    pdf.ln(6)
    pdf.set_font("helvetica", "I", 8)
    pdf.set_text_color(100, 116, 139)
    pdf.multi_cell(0, 4, "* Catatan: Nilai R2 menggambarkan persentase pengaruh parameter demografi di atas terhadap variasi tingkat partisipasi politik. RMSE yang semakin mendekati 0 menunjukkan keakuratan prediksi model yang semakin tinggi.", align="L")
    
    # Return PDF bytes
    return bytes(pdf.output())
