from fpdf import FPDF
from datetime import datetime
import os

class ViolationPDF(FPDF):
    def header(self):
        # Add logo at the top center
        logo_path = os.path.join(os.path.dirname(__file__), "..", "static", "images", "ai_logo.png")
        if os.path.exists(logo_path):
            self.image(logo_path, x=80, y=10, w=50)  # Centered, adjust w as needed
            self.ln(35)  # Space below logo
        self.set_font("Arial", "B", 14)
        self.cell(0, 10, "HOA Violation Summary", border=False, ln=True, align="C")
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")

    def violation_body(self, violation: dict):
        self.set_font("Arial", "", 12)
        
        # Violation header information
        self.cell(40, 10, f"Violation #: {violation.get('violation_number', 'N/A')}", ln=True)
        self.cell(40, 10, f"Date: {violation.get('timestamp', 'N/A')}", ln=True)
        self.cell(40, 10, f"Inspected by: {violation.get('username', 'N/A')}", ln=True)
        self.cell(40, 10, f"HOA: {violation.get('hoa', 'N/A')}", ln=True)
        self.cell(40, 10, f"Address: {violation.get('address', 'N/A')}", ln=True)
        self.cell(40, 10, f"Location: {violation.get('location', 'N/A')}", ln=True)
        self.cell(40, 10, f"Resident: {violation.get('offender', 'N/A')}", ln=True)
        self.cell(40, 10, f"Status: {violation.get('status', 'Open')}", ln=True)
        self.cell(40, 10, f"Tags: {violation.get('tags', 'N/A')}", ln=True)
        
        # GPS coordinates if available
        if violation.get('gps_coordinates'):
            self.cell(40, 10, f"GPS: {violation.get('gps_coordinates', 'N/A')}", ln=True)
        
        self.ln(5)
        
        # Violation description
        self.multi_cell(0, 10, f"Description:\n{violation.get('description', 'N/A')}")
        self.ln(5)
        
        # AI-generated summary
        self.multi_cell(0, 10, f"AI Summary:\n{violation.get('summary', 'N/A')}")
        self.ln(10)
        
        # Include image if available
        if violation.get("image_path") and os.path.exists(violation["image_path"]):
            self.image(violation["image_path"], w=100)
            self.ln(10)

def generate_pdf(violation: dict, output_dir="static/reports") -> str:
    os.makedirs(output_dir, exist_ok=True)
    pdf = ViolationPDF()
    pdf.add_page()
    pdf.violation_body(violation)
    filename = f"violation_{violation.get('id', 'unknown')}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
    pdf_path = os.path.join(output_dir, filename)
    pdf.output(pdf_path)
    return pdf_path
