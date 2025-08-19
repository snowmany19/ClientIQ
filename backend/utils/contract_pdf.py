# backend/utils/contract_pdf.py
# ContractGuard.ai - Contract Analysis PDF Generator

from fpdf import FPDF
from datetime import datetime
import os
import json
from typing import Dict, List, Any
from models import ContractRecord

class ContractAnalysisPDF(FPDF):
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=15)
        
        # Try to add a font, with fallbacks for different systems
        font_paths = [
            '/System/Library/Fonts/Arial.ttf',  # macOS
            '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',  # Linux
            '/usr/share/fonts/TTF/Arial.ttf',  # Some Linux systems
            'arial.ttf'  # Windows fallback
        ]
        
        font_added = False
        for font_path in font_paths:
            try:
                if os.path.exists(font_path):
                    self.add_font('DejaVu', '', font_path, uni=True)
                    font_added = True
                    break
            except Exception:
                continue
        
        if not font_added:
            # Use default font if no custom font can be loaded
            print("Warning: Could not load custom font, using default")
        
    def header(self):
        # Add logo at the top center (optional)
        logo_path = os.path.join(os.path.dirname(__file__), "..", "static", "images", "ai_logo.png")
        if os.path.exists(logo_path):
            try:
                self.image(logo_path, x=80, y=10, w=50)
                self.ln(35)
            except Exception:
                # If logo fails to load, just continue without it
                self.ln(25)
        else:
            # No logo, just add some spacing
            self.ln(25)
        
        self.set_font("Arial", "B", 16)
        self.cell(0, 10, "ContractGuard.ai - Contract Analysis Report", border=False, ln=True, align="C")
        self.ln(5)
        
        # Add report metadata
        self.set_font("Arial", "", 10)
        self.cell(0, 8, f"Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", ln=True, align="C")
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.cell(0, 10, f"Page {self.page_no()} - ContractGuard.ai", align="C")

    def add_section_title(self, title: str, level: int = 1):
        """Add a section title with appropriate formatting."""
        try:
            if level == 1:
                self.set_font("DejaVu", "B", 14)
                self.set_fill_color(240, 240, 240)
                self.cell(0, 10, title, ln=True, fill=True)
            elif level == 2:
                self.set_font("DejaVu", "B", 12)
                self.cell(0, 8, title, ln=True)
            else:
                self.set_font("DejaVu", "B", 10)
                self.cell(0, 6, title, ln=True)
        except Exception:
            # Fallback to default font
            if level == 1:
                self.set_font("Arial", "B", 14)
                self.set_fill_color(240, 240, 240)
                self.cell(0, 10, title, ln=True, fill=True)
            elif level == 2:
                self.set_font("Arial", "B", 12)
                self.cell(0, 8, title, ln=True)
            else:
                self.set_font("Arial", "B", 10)
                self.cell(0, 6, title, ln=True)
        self.ln(2)

    def add_contract_info(self, contract: ContractRecord):
        """Add contract basic information."""
        self.add_section_title("Contract Information", 1)
        
        # Create a table-like layout for contract details
        try:
            self.set_font("DejaVu", "B", 10)
        except Exception:
            self.set_font("Arial", "B", 10)
            
        self.cell(40, 8, "Title:", ln=False)
        try:
            self.set_font("DejaVu", "", 10)
        except Exception:
            self.set_font("Arial", "", 10)
        self.cell(0, 8, contract.title, ln=True)
        
        try:
            self.set_font("DejaVu", "B", 10)
        except Exception:
            self.set_font("Arial", "B", 10)
        self.cell(40, 8, "Counterparty:", ln=False)
        try:
            self.set_font("DejaVu", "", 10)
        except Exception:
            self.set_font("Arial", "", 10)
        self.cell(0, 8, contract.counterparty, ln=True)
        
        try:
            self.set_font("DejaVu", "B", 10)
        except Exception:
            self.set_font("Arial", "B", 10)
        self.cell(40, 8, "Category:", ln=False)
        try:
            self.set_font("DejaVu", "", 10)
        except Exception:
            self.set_font("Arial", "", 10)
        self.cell(0, 8, contract.category, ln=True)
        
        if contract.effective_date:
            try:
                self.set_font("DejaVu", "B", 10)
            except Exception:
                self.set_font("Arial", "B", 10)
            self.cell(40, 8, "Effective Date:", ln=False)
            try:
                self.set_font("DejaVu", "", 10)
            except Exception:
                self.set_font("Arial", "", 10)
            self.cell(0, 8, contract.effective_date.strftime('%B %d, %Y'), ln=True)
        
        if contract.term_end:
            try:
                self.set_font("DejaVu", "B", 10)
            except Exception:
                self.set_font("Arial", "B", 10)
            self.cell(40, 8, "Term End:", ln=False)
            try:
                self.set_font("DejaVu", "", 10)
            except Exception:
                self.set_font("Arial", "", 10)
            self.cell(0, 8, contract.term_end.strftime('%B %d, %Y'), ln=True)
        
        if contract.governing_law:
            try:
                self.set_font("DejaVu", "B", 10)
            except Exception:
                self.set_font("Arial", "B", 10)
            self.cell(40, 8, "Governing Law:", ln=False)
            try:
                self.set_font("DejaVu", "", 10)
            except Exception:
                self.set_font("Arial", "", 10)
            self.cell(0, 8, contract.governing_law, ln=True)
        
        try:
            self.set_font("DejaVu", "B", 10)
        except Exception:
            self.set_font("Arial", "B", 10)
        self.cell(40, 8, "Status:", ln=False)
        try:
            self.set_font("DejaVu", "", 10)
        except Exception:
            self.set_font("Arial", "", 10)
        self.cell(0, 8, contract.status.title(), ln=True)
        
        try:
            self.set_font("DejaVu", "B", 10)
        except Exception:
            self.set_font("Arial", "B", 10)
        self.cell(40, 8, "Analysis Date:", ln=False)
        try:
            self.set_font("DejaVu", "", 10)
        except Exception:
            self.set_font("Arial", "", 10)
        self.cell(0, 8, contract.updated_at.strftime('%B %d, %Y at %I:%M %p'), ln=True)
        
        self.ln(5)

    def add_executive_summary(self, summary_text: str):
        """Add the executive summary section."""
        self.add_section_title("Executive Summary", 1)
        
        self.set_font("Arial", "", 11)
        self.multi_cell(0, 6, summary_text)
        self.ln(5)

    def add_key_terms(self, key_terms: Dict[str, Any]):
        """Add key terms section."""
        self.add_section_title("Key Terms", 1)
        
        if not key_terms:
            self.set_font("Arial", "", 10)
            self.cell(0, 8, "No key terms identified.", ln=True)
            return
        
        for term, value in key_terms.items():
            if value and str(value).strip():
                self.set_font("Arial", "B", 10)
                term_display = term.replace('_', ' ').title()
                self.cell(50, 8, f"{term_display}:", ln=False)
                self.set_font("Arial", "", 10)
                self.multi_cell(0, 8, str(value))
                self.ln(2)

    def add_risk_analysis(self, risks: List[Dict[str, Any]]):
        """Add risk analysis section."""
        self.add_section_title("Risk Analysis", 1)
        
        if not risks:
            self.set_font("Arial", "", 10)
            self.cell(0, 8, "No significant risks identified in this contract.", ln=True)
            return
        
        # Risk summary table
        self.add_section_title("Risk Summary", 2)
        self.set_font("Arial", "B", 9)
        self.cell(60, 8, "Risk", border=1, ln=False)
        self.cell(20, 8, "Severity", border=1, ln=False)
        self.cell(20, 8, "Category", border=1, ln=False)
        self.cell(0, 8, "Description", border=1, ln=True)
        
        self.set_font("Arial", "", 9)
        for risk in risks:
            # Risk title (truncated if too long)
            title = risk.get('title', 'Unknown Risk')
            if len(title) > 25:
                title = title[:22] + "..."
            self.cell(60, 8, title, border=1, ln=False)
            
            # Severity
            severity = risk.get('severity', 0)
            severity_text = f"Level {severity}"
            self.cell(20, 8, severity_text, border=1, ln=False)
            
            # Category
            category = risk.get('category', 'General')
            if len(category) > 15:
                category = category[:12] + "..."
            self.cell(20, 8, category, border=1, ln=False)
            
            # Description (truncated)
            description = risk.get('description', 'No description')
            if len(description) > 50:
                description = description[:47] + "..."
            self.cell(0, 8, description, border=1, ln=True)
        
        self.ln(5)
        
        # Detailed risk analysis
        self.add_section_title("Detailed Risk Analysis", 2)
        for i, risk in enumerate(risks, 1):
            self.set_font("Arial", "B", 10)
            self.cell(0, 8, f"Risk {i}: {risk.get('title', 'Unknown Risk')}", ln=True)
            
            self.set_font("Arial", "", 9)
            self.cell(20, 6, "Severity:", ln=False)
            self.cell(0, 6, f"Level {risk.get('severity', 0)} (Confidence: {risk.get('confidence', 0):.1%})", ln=True)
            
            self.cell(20, 6, "Category:", ln=False)
            self.cell(0, 6, risk.get('category', 'General'), ln=True)
            
            if risk.get('clause_reference'):
                self.cell(20, 6, "Reference:", ln=False)
                self.cell(0, 6, risk.get('clause_reference'), ln=True)
            
            self.cell(0, 6, "Description:", ln=True)
            self.multi_cell(0, 6, risk.get('description', 'No description provided'))
            
            self.cell(0, 6, "Rationale:", ln=True)
            self.multi_cell(0, 6, risk.get('rationale', 'No rationale provided'))
            
            self.cell(0, 6, "Business Impact:", ln=True)
            self.multi_cell(0, 6, risk.get('business_impact', 'No impact assessment provided'))
            
            if risk.get('mitigation_suggestions'):
                self.cell(0, 6, "Mitigation Suggestions:", ln=True)
                for suggestion in risk.get('mitigation_suggestions', []):
                    self.cell(10, 6, "•", ln=False)
                    self.multi_cell(0, 6, suggestion)
            
            self.ln(3)

    def add_rewrite_suggestions(self, suggestions: List[Dict[str, Any]]):
        """Add rewrite suggestions section."""
        self.add_section_title("Rewrite Suggestions", 1)
        
        if not suggestions:
            self.set_font("Arial", "", 10)
            self.cell(0, 8, "No rewrite suggestions available for this contract.", ln=True)
            return
        
        for i, suggestion in enumerate(suggestions, 1):
            self.set_font("Arial", "B", 10)
            suggestion_type = suggestion.get('type', 'balanced').title()
            self.cell(0, 8, f"Suggestion {i}: {suggestion_type} Approach", ln=True)
            
            self.set_font("Arial", "", 9)
            self.cell(20, 6, "Category:", ln=False)
            self.cell(0, 6, suggestion.get('category', 'General'), ln=True)
            
            if suggestion.get('original_text'):
                self.cell(0, 6, "Original Text:", ln=True)
                self.set_font("Arial", "I", 8)
                self.multi_cell(0, 5, suggestion.get('original_text'))
                self.set_font("Arial", "", 9)
            
            self.cell(0, 6, "Suggested Text:", ln=True)
            self.set_font("Arial", "B", 8)
            self.multi_cell(0, 5, suggestion.get('suggested_text', 'No suggestion provided'))
            self.set_font("Arial", "", 9)
            
            self.cell(0, 6, "Rationale:", ln=True)
            self.multi_cell(0, 6, suggestion.get('rationale', 'No rationale provided'))
            
            if suggestion.get('negotiation_tips'):
                self.cell(0, 6, "Negotiation Tips:", ln=True)
                for tip in suggestion.get('negotiation_tips', []):
                    self.cell(10, 6, "•", ln=False)
                    self.multi_cell(0, 6, tip)
            
            if suggestion.get('fallback_position'):
                self.cell(0, 6, "Fallback Position:", ln=True)
                self.multi_cell(0, 6, suggestion.get('fallback_position'))
            
            self.ln(3)

    def add_compliance_analysis(self, compliance: Dict[str, Any]):
        """Add compliance analysis section."""
        self.add_section_title("Compliance Analysis", 1)
        
        if not compliance:
            self.set_font("Arial", "", 10)
            self.cell(0, 8, "No compliance analysis available.", ln=True)
            return
        
        # Regulatory risks
        if compliance.get('regulatory_risks'):
            self.add_section_title("Regulatory Risks", 2)
            for risk in compliance.get('regulatory_risks', []):
                self.set_font("Arial", "B", 9)
                self.cell(0, 6, f"{risk.get('regulation', 'Unknown Regulation')}", ln=True)
                self.set_font("Arial", "", 8)
                self.cell(0, 5, f"Issue: {risk.get('issue', 'No issue description')}", ln=True)
                self.cell(0, 5, f"Severity: {risk.get('severity', 'Unknown')}", ln=True)
                self.cell(0, 5, f"Recommendation: {risk.get('recommendation', 'No recommendation')}", ln=True)
                self.ln(2)
        
        # Data privacy
        if compliance.get('data_privacy'):
            self.add_section_title("Data Privacy Considerations", 2)
            self.set_font("Arial", "", 9)
            self.multi_cell(0, 6, compliance.get('data_privacy', 'No data privacy analysis available'))
            self.ln(2)
        
        # Employment law
        if compliance.get('employment_law'):
            self.add_section_title("Employment Law Considerations", 2)
            self.set_font("Arial", "", 9)
            self.multi_cell(0, 6, compliance.get('employment_law', 'No employment law analysis available'))
            self.ln(2)
        
        # IP considerations
        if compliance.get('intellectual_property'):
            self.add_section_title("Intellectual Property Considerations", 2)
            self.set_font("Arial", "", 9)
            self.multi_cell(0, 6, compliance.get('intellectual_property', 'No IP analysis available'))
            self.ln(2)
        
        # Tax implications
        if compliance.get('tax_implications'):
            self.add_section_title("Tax Implications", 2)
            self.set_font("Arial", "", 9)
            self.multi_cell(0, 6, compliance.get('tax_implications', 'No tax analysis available'))
            self.ln(2)

    def add_category_analysis(self, category_analysis: Dict[str, Any]):
        """Add category-specific analysis."""
        self.add_section_title("Category-Specific Analysis", 1)
        
        if not category_analysis:
            self.set_font("Arial", "", 10)
            self.cell(0, 8, "No category-specific analysis available.", ln=True)
            return
        
        if category_analysis.get('category_insights'):
            self.add_section_title("Category Insights", 2)
            self.set_font("Arial", "", 9)
            self.multi_cell(0, 6, category_analysis.get('category_insights'))
            self.ln(2)
        
        if category_analysis.get('industry_standards'):
            self.add_section_title("Industry Standards Comparison", 2)
            self.set_font("Arial", "", 9)
            self.multi_cell(0, 6, category_analysis.get('industry_standards'))
            self.ln(2)
        
        if category_analysis.get('missing_elements'):
            self.add_section_title("Missing Elements", 2)
            self.set_font("Arial", "", 9)
            for element in category_analysis.get('missing_elements', []):
                self.cell(10, 6, "•", ln=False)
                self.multi_cell(0, 6, element)
            self.ln(2)
        
        if category_analysis.get('red_flags'):
            self.add_section_title("Red Flags", 2)
            self.set_font("Arial", "", 9)
            for flag in category_analysis.get('red_flags', []):
                self.cell(10, 6, "•", ln=False)
                self.multi_cell(0, 6, flag)
            self.ln(2)

    def add_appendix(self, contract: ContractRecord):
        """Add appendix with contract metadata."""
        self.add_page()
        self.add_section_title("Appendix", 1)
        
        self.set_font("Arial", "B", 10)
        self.cell(0, 8, "Contract Metadata", ln=True)
        self.set_font("Arial", "", 9)
        
        self.cell(40, 6, "Contract ID:", ln=False)
        self.cell(0, 6, str(contract.id), ln=True)
        
        self.cell(40, 6, "Created:", ln=False)
        self.cell(0, 6, contract.created_at.strftime('%B %d, %Y at %I:%M %p'), ln=True)
        
        self.cell(40, 6, "Last Updated:", ln=False)
        self.cell(0, 6, contract.updated_at.strftime('%B %d, %Y at %I:%M %p'), ln=True)
        
        if hasattr(contract, 'owner') and contract.owner and hasattr(contract.owner, 'username'):
            self.cell(40, 6, "Owner:", ln=False)
            self.cell(0, 6, contract.owner.username, ln=True)
        
        if contract.uploaded_files:
            self.cell(40, 6, "Files:", ln=True)
            for file_path in contract.uploaded_files:
                filename = os.path.basename(file_path)
                self.cell(10, 6, "•", ln=False)
                self.cell(0, 6, filename, ln=True)

def generate_contract_analysis_pdf(contract: ContractRecord, output_dir="static/reports") -> str:
    """Generate a comprehensive contract analysis PDF report."""
    os.makedirs(output_dir, exist_ok=True)
    
    pdf = ContractAnalysisPDF()
    pdf.add_page()
    
    # Add contract information
    pdf.add_contract_info(contract)
    
    # Add executive summary
    if contract.summary_text:
        pdf.add_executive_summary(contract.summary_text)
    
    # Add key terms if available
    if contract.analysis_json and contract.analysis_json.get('summary', {}).get('key_terms'):
        pdf.add_key_terms(contract.analysis_json['summary']['key_terms'])
    
    # Add risk analysis
    if contract.risk_items:
        pdf.add_risk_analysis(contract.risk_items)
    
    # Add rewrite suggestions
    if contract.rewrite_suggestions:
        pdf.add_rewrite_suggestions(contract.rewrite_suggestions)
    
    # Add compliance analysis
    if contract.analysis_json and contract.analysis_json.get('compliance'):
        pdf.add_compliance_analysis(contract.analysis_json['compliance'])
    
    # Add category analysis
    if contract.analysis_json and contract.analysis_json.get('category_analysis'):
        pdf.add_category_analysis(contract.analysis_json['category_analysis'])
    
    # Add appendix
    pdf.add_appendix(contract)
    
    # Generate filename and save
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"contract_analysis_{contract.id}_{timestamp}.pdf"
    pdf_path = os.path.join(output_dir, filename)
    pdf.output(pdf_path)
    
    return pdf_path
