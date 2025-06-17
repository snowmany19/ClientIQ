from fpdf import FPDF
from datetime import datetime
import os

class IncidentPDF(FPDF):
    def header(self):
        self.set_font("Arial", "B", 14)
        self.cell(0, 10, "Incident Report", border=False, ln=True, align="C")
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")

    def incident_body(self, incident: dict):
        self.set_font("Arial", "", 12)
        self.cell(40, 10, f"Date: {incident.get('timestamp', 'N/A')}", ln=True)
        self.cell(40, 10, f"Reported by: {incident.get('username', 'N/A')}", ln=True)
        self.cell(40, 10, f"Store: {incident.get('store', 'N/A')}", ln=True)
        self.cell(40, 10, f"Tags: {incident.get('tags', 'N/A')}", ln=True)
        self.ln(5)
        self.multi_cell(0, 10, f"Description:\n{incident.get('description', 'N/A')}")
        self.ln(5)
        self.multi_cell(0, 10, f"AI Summary:\n{incident.get('summary', 'N/A')}")
        self.ln(10)
        if incident.get("image_path") and os.path.exists(incident["image_path"]):
            self.image(incident["image_path"], w=100)
            self.ln(10)

def generate_pdf(incident: dict, output_dir="static/reports") -> str:
    os.makedirs(output_dir, exist_ok=True)
    pdf = IncidentPDF()
    pdf.add_page()
    pdf.incident_body(incident)
    filename = f"incident_{incident.get('id', 'unknown')}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
    pdf_path = os.path.join(output_dir, filename)
    pdf.output(pdf_path)
    return pdf_path
