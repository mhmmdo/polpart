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
    pdf.set_font("helvetica", "B", 14)
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
    pdf.cell(col_width, 6, f"Lokasi Wilayah: Kec. {data.get('kecamatan', '-')}", ln=False)
    pdf.cell(col_width, 6, f"Kelurahan / Desa: {data.get('kelurahan', '-')}", ln=True)
    
    # Line 3
    pdf.cell(col_width, 6, f"Nomor TPS: {data.get('no_tps', '-')}", ln=False)
    pdf.cell(col_width, 6, "Metode Analisa: Random Forest Regressor", ln=True)
    
    pdf.ln(6)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(6)
    
    # Input Variables Header
    pdf.set_font("helvetica", "B", 11)
    pdf.set_text_color(30, 41, 59)
    pdf.cell(0, 8, "1. Parameter Demografi & Lokasi (Variabel Input)", ln=True)
    pdf.ln(2)
    
    # Table of inputs
    pdf.set_font("helvetica", "B", 10)
    pdf.set_fill_color(234, 248, 248) # Mint
    pdf.set_text_color(30, 41, 59)
    
    pdf.cell(100, 8, " Nama Variabel / Kolom", border=1, fill=True, align="L")
    pdf.cell(90, 8, " Nilai / Angka Input", border=1, fill=True, align="C", ln=True)
    
    pdf.set_font("helvetica", "", 10)
    
    # Row 1
    pdf.cell(100, 8, " Jumlah Daftar Pemilih Tetap (DPT) TPS", border=1, align="L")
    pdf.cell(90, 8, f" {data.get('dpt', 0):,}".replace(",", "."), border=1, align="C", ln=True)
    
    # Row 2
    pdf.cell(100, 8, " Rasio DPT Terhadap Penduduk Kelurahan", border=1, align="L")
    pdf.cell(90, 8, f" {data.get('rasio_dpt', 0.0):.4f}", border=1, align="C", ln=True)
    
    # Row 3
    pdf.cell(100, 8, " Persentase Pemilih Usia 17 - 24 Tahun (Kecamatan)", border=1, align="L")
    pdf.cell(90, 8, f" {data.get('usia_17_24', 0.0):.2f}%", border=1, align="C", ln=True)
    
    # Row 4
    pdf.cell(100, 8, " Persentase Pemilih Usia 25 - 44 Tahun (Kecamatan)", border=1, align="L")
    pdf.cell(90, 8, f" {data.get('usia_25_44', 0.0):.2f}%", border=1, align="C", ln=True)
    
    # Row 5
    pdf.cell(100, 8, " Persentase Pemilih Usia 45 Tahun Keatas (Kecamatan)", border=1, align="L")
    pdf.cell(90, 8, f" {data.get('usia_45_plus', 0.0):.2f}%", border=1, align="C", ln=True)
    
    pdf.ln(10)
    
    # Prediction Results Box
    pdf.set_fill_color(254, 243, 199) # Pale yellow-orange alert-box
    pdf.rect(10, pdf.get_y(), 190, 24, "F")
    
    pdf.set_y(pdf.get_y() + 4)
    pdf.set_font("helvetica", "B", 11)
    pdf.set_text_color(180, 83, 9) # Amber text
    pdf.cell(0, 5, "    OUTPUT PREDIKSI MODEL:", ln=True, align="L")
    
    pdf.set_font("helvetica", "B", 15)
    pdf.set_text_color(220, 38, 38) # Red/Coral warning
    hasil_str = f"{data.get('hasil_prediksi', 0.0):.2f}%"
    pdf.cell(0, 10, f"    Tingkat Partisipasi Politik Prediksi: {hasil_str}", ln=True, align="L")
    
    pdf.ln(10)
    
    # Model evaluation metrics
    pdf.set_font("helvetica", "B", 11)
    pdf.set_text_color(30, 41, 59)
    pdf.cell(0, 8, "2. Performa Model Acuan (Random Forest Regressor)", ln=True)
    pdf.ln(2)
    
    metrics = data.get("model_metrics", {})
    r2 = metrics.get("r2", 0.0)
    rmse = metrics.get("rmse", 0.0)
    
    pdf.set_font("helvetica", "", 10)
    pdf.cell(50, 8, " Koefisien Determinasi (R2 Score)", border=1, align="L")
    pdf.cell(45, 8, f" {r2:.4f} ({r2*100:.1f}%)", border=1, align="C")
    
    pdf.cell(50, 8, " Root Mean Squared Error (RMSE)", border=1, align="L")
    pdf.cell(45, 8, f" {rmse:.4f}", border=1, align="C", ln=True)
    
    pdf.ln(5)
    pdf.set_font("helvetica", "I", 8)
    pdf.set_text_color(100, 116, 139)
    pdf.multi_cell(0, 4, "* Catatan: Nilai R2 menggambarkan persentase pengaruh parameter demografi di atas terhadap variasi tingkat partisipasi politik. RMSE yang semakin mendekati 0 menunjukkan keakuratan prediksi model yang semakin tinggi.", align="L")
    
    # Official Signature space
    pdf.ln(15)
    pdf.set_font("helvetica", "", 10)
    pdf.set_text_color(30, 41, 59)
    
    pdf.cell(120, 6, "", ln=False)
    pdf.cell(70, 6, "Disetujui / Disahkan,", ln=True, align="C")
    pdf.ln(15)
    
    pdf.cell(120, 6, "", ln=False)
    pdf.set_font("helvetica", "B", 10)
    pdf.cell(70, 6, f"({data.get('printed_by', 'Operator KPU')})", ln=True, align="C")
    pdf.set_font("helvetica", "", 9)
    pdf.cell(120, 6, "", ln=False)
    pdf.cell(70, 6, "Sistem Analisa PolPart RF", ln=True, align="C")
    
    # Return PDF bytes
    return bytes(pdf.output())
