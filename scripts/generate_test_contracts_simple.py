#!/usr/bin/env python3
"""
Generate Test Contracts for ContractGuard.ai (Simplified Version)
Creates realistic test contracts for all 7 contract types and runs them through analysis
"""

import os
import sys
import json
import random
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any

# Add backend to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

# Mock company names for variety
COMPANIES = [
    "TechCorp", "InnovateLabs", "DataSecure", "CloudTech", "FutureSystems",
    "ServicePro", "ConsultingCorp", "ExpertSolutions", "ProfessionalPartners", "ServiceHub",
    "ProjectCorp", "BuildTech", "DesignSolutions", "ImplementationPro", "ProjectHub",
    "EmployCorp", "WorkTech", "CareerSolutions", "JobHub", "EmploymentPro",
    "VendorCorp", "SupplyTech", "ProviderSolutions", "VendorHub", "SupplyPro",
    "LeaseCorp", "RentTech", "PropertySolutions", "LeaseHub", "RentPro",
    "OtherCorp", "BusinessTech", "PartnershipSolutions", "OtherHub", "BusinessPro"
]

# Contract Templates with randomization
CONTRACT_TEMPLATES = {
    "NDA": {
        "title_prefixes": ["Confidentiality Agreement", "Non-Disclosure Agreement", "Proprietary Information Agreement"],
        "focus_areas": ["software development", "research collaboration", "business partnership", "technology licensing"],
        "terms": ["2 years", "3 years", "5 years", "perpetual", "until termination"],
        "penalties": ["$100,000", "$250,000", "$500,000", "actual damages", "liquidated damages"]
    },
    "MSA": {
        "title_prefixes": ["Master Services Agreement", "Service Agreement", "Professional Services Agreement"],
        "focus_areas": ["IT consulting", "marketing services", "legal services", "accounting services", "engineering services"],
        "terms": ["1 year", "2 years", "3 years", "5 years", "auto-renewing"],
        "payment_terms": ["Net 30", "Net 45", "Net 60", "50% upfront", "monthly billing"]
    },
    "SOW": {
        "title_prefixes": ["Statement of Work", "Project Agreement", "Work Order", "Service Description"],
        "focus_areas": ["website development", "mobile app development", "system integration", "consulting project", "design project"],
        "deliverables": ["functional website", "mobile application", "system documentation", "training materials", "final report"],
        "timelines": ["30 days", "60 days", "90 days", "6 months", "1 year"]
    },
    "Employment": {
        "title_prefixes": ["Employment Agreement", "Employment Contract", "Offer Letter", "Work Agreement"],
        "positions": ["Software Engineer", "Marketing Manager", "Sales Representative", "Product Manager", "Data Analyst"],
        "compensation_types": ["salary", "hourly", "commission-based", "salary + bonus", "equity + salary"],
        "benefits": ["health insurance", "dental insurance", "401k", "stock options", "flexible PTO"]
    },
    "Vendor": {
        "title_prefixes": ["Vendor Agreement", "Supplier Contract", "Service Provider Agreement", "Vendor Services Agreement"],
        "services": ["office supplies", "cleaning services", "IT equipment", "marketing materials", "logistics services"],
        "performance_metrics": ["99% uptime", "24-hour response", "same-day delivery", "quality guarantee", "SLA compliance"],
        "payment_terms": ["Net 30", "Net 45", "Net 60", "monthly billing", "quarterly billing"]
    },
    "Lease": {
        "title_prefixes": ["Lease Agreement", "Rental Contract", "Property Lease", "Space Rental Agreement"],
        "property_types": ["office space", "retail space", "warehouse", "apartment", "commercial building"],
        "lease_terms": ["1 year", "2 years", "3 years", "5 years", "month-to-month"],
        "utilities": ["electricity", "water", "gas", "internet", "all utilities included"]
    },
    "Other": {
        "title_prefixes": ["Service Agreement", "Business Agreement", "Partnership Agreement", "Collaboration Agreement"],
        "agreement_types": ["partnership", "collaboration", "joint venture", "licensing", "distribution"],
        "focus_areas": ["business development", "market expansion", "technology transfer", "research collaboration", "marketing partnership"]
    }
}

def generate_random_date(start_year_offset: int = -1, end_year_offset: int = 1) -> datetime:
    """Generate a random date within the specified year range."""
    start_date = datetime.now() + timedelta(days=start_year_offset * 365)
    end_date = datetime.now() + timedelta(days=end_year_offset * 365)
    
    days_between = (end_date - start_date).days
    random_days = random.randint(0, days_between)
    return start_date + timedelta(days=random_days)

def generate_contract_content(category: str) -> Dict[str, Any]:
    """Generate randomized contract content for a specific category."""
    template = CONTRACT_TEMPLATES[category]
    
    # Generate company names
    company1 = random.choice(COMPANIES)
    company2 = random.choice(COMPANIES)
    while company2 == company1:
        company2 = random.choice(COMPANIES)
    
    # Generate dates
    start_date = generate_random_date(-1, 1)
    end_date = start_date + timedelta(days=random.randint(365, 1825))  # 1-5 years
    
    # Generate contract-specific content
    if category == "NDA":
        content = generate_nda_content(template, company1, company2, start_date, end_date)
    elif category == "MSA":
        content = generate_msa_content(template, company1, company2, start_date, end_date)
    elif category == "SOW":
        content = generate_sow_content(template, company1, company2, start_date, end_date)
    elif category == "Employment":
        content = generate_employment_content(template, company1, company2, start_date, end_date)
    elif category == "Vendor":
        content = generate_vendor_content(template, company1, company2, start_date, end_date)
    elif category == "Lease":
        content = generate_lease_content(template, company1, company2, start_date, end_date)
    else:
        content = generate_other_content(template, company1, company2, start_date, end_date)
    
    return {
        "title": f"{random.choice(template['title_prefixes'])} - {company1} and {company2}",
        "counterparty": company2,
        "category": category,
        "effective_date": start_date.strftime("%Y-%m-%d"),
        "term_end": end_date.strftime("%Y-%m-%d"),
        "governing_law": random.choice(["California", "New York", "Delaware", "Texas", "Florida"]),
        "content": content
    }

def generate_nda_content(template: Dict, company1: str, company2: str, start_date: datetime, end_date: datetime) -> str:
    """Generate NDA contract content."""
    term = random.choice(template["terms"])
    penalty = random.choice(template["penalties"])
    focus = random.choice(template["focus_areas"])
    
    return f"""
NON-DISCLOSURE AGREEMENT

This Non-Disclosure Agreement (the "Agreement") is entered into as of {start_date.strftime('%B %d, %Y')} by and between {company1}, a corporation organized under the laws of the State of California ("Disclosing Party"), and {company2}, a corporation organized under the laws of the State of Delaware ("Receiving Party").

1. CONFIDENTIAL INFORMATION
The Receiving Party acknowledges that it may receive confidential and proprietary information related to {focus} including, but not limited to, technical specifications, business plans, customer lists, and trade secrets.

2. NON-DISCLOSURE OBLIGATIONS
The Receiving Party agrees to maintain the confidentiality of all Confidential Information and not to disclose such information to any third party without the prior written consent of the Disclosing Party.

3. TERM AND TERMINATION
This Agreement shall remain in effect for {term} from the effective date. The confidentiality obligations shall survive termination for an additional {term}.

4. REMEDIES
In the event of a breach of this Agreement, the Receiving Party shall be liable for damages up to {penalty} and the Disclosing Party may seek injunctive relief.

5. RETURN OF MATERIALS
Upon termination, the Receiving Party shall return all confidential materials to the Disclosing Party or destroy them as directed.

IN WITNESS WHEREOF, the parties have executed this Agreement as of the date first above written.

{company1}                                    {company2}
By: ___________________________    By: ___________________________
Title: _________________________    Title: _________________________
Date: __________________________    Date: ___________________________
"""

def generate_msa_content(template: Dict, company1: str, company2: str, start_date: datetime, end_date: datetime) -> str:
    """Generate MSA contract content."""
    term = random.choice(template["terms"])
    payment = random.choice(template["payment_terms"])
    focus = random.choice(template["focus_areas"])
    
    return f"""
MASTER SERVICES AGREEMENT

This Master Services Agreement (the "Agreement") is entered into as of {start_date.strftime('%B %d, %Y')} by and between {company1}, a corporation organized under the laws of the State of California ("Client"), and {company2}, a corporation organized under the laws of the State of Delaware ("Service Provider").

1. SERVICES
Service Provider shall provide {focus} services as described in individual Statements of Work ("SOW") executed by both parties.

2. TERM
This Agreement shall commence on the effective date and continue for {term}, unless earlier terminated as provided herein.

3. PAYMENT TERMS
Client shall pay Service Provider according to the payment terms specified in each SOW. Standard payment terms are {payment}.

4. PERFORMANCE STANDARDS
Service Provider shall perform all services in a professional and workmanlike manner, consistent with industry standards.

5. LIABILITY LIMITATION
Neither party shall be liable for any indirect, incidental, special, or consequential damages arising out of this Agreement.

6. TERMINATION
Either party may terminate this Agreement upon 30 days written notice to the other party.

IN WITNESS WHEREOF, the parties have executed this Agreement as of the date first above written.

{company1}                                    {company2}
By: ___________________________    By: ___________________________
Title: _________________________    Title: _________________________
Date: __________________________    Date: ___________________________
"""

def generate_sow_content(template: Dict, company1: str, company2: str, start_date: datetime, end_date: datetime) -> str:
    """Generate SOW contract content."""
    deliverable = random.choice(template["deliverables"])
    timeline = random.choice(template["timelines"])
    focus = random.choice(template["focus_areas"])
    
    return f"""
STATEMENT OF WORK

This Statement of Work ("SOW") is entered into as of {start_date.strftime('%B %d, %Y')} by and between {company1}, a corporation organized under the laws of the State of California ("Client"), and {company2}, a corporation organized under the laws of the State of Delaware ("Service Provider").

1. PROJECT DESCRIPTION
Service Provider shall develop and deliver {deliverable} for Client's {focus} needs.

2. DELIVERABLES
- Project plan and timeline
- {deliverable}
- User documentation
- Training materials
- Final project report

3. TIMELINE
Project shall be completed within {timeline} from the effective date.

4. ACCEPTANCE CRITERIA
Deliverables shall be accepted upon Client's written approval or 5 business days after delivery if no objections are raised.

5. CHANGE MANAGEMENT
Any changes to this SOW must be approved in writing by both parties.

6. PAYMENT SCHEDULE
- 25% upon project initiation
- 50% upon delivery of major milestones
- 25% upon final acceptance

IN WITNESS WHEREOF, the parties have executed this SOW as of the date first above written.

{company1}                                    {company2}
By: ___________________________    By: ___________________________
Title: _________________________    Title: _________________________
Date: __________________________    Date: ___________________________
"""

def generate_employment_content(template: Dict, company1: str, company2: str, start_date: datetime, end_date: datetime) -> str:
    """Generate Employment contract content."""
    position = random.choice(template["positions"])
    compensation = random.choice(template["compensation_types"])
    benefits = random.choice(template["benefits"])
    
    return f"""
EMPLOYMENT AGREEMENT

This Employment Agreement (the "Agreement") is entered into as of {start_date.strftime('%B %d, %Y')} by and between {company1}, a corporation organized under the laws of the State of California ("Employer"), and {company2}, an individual ("Employee").

1. POSITION AND DUTIES
Employee shall serve as {position} and shall perform all duties and responsibilities associated with such position.

2. COMPENSATION
Employee shall receive compensation in the form of {compensation} as determined by Employer, subject to periodic review and adjustment.

3. BENEFITS
Employee shall be eligible for standard employee benefits including {benefits}, subject to Employer's benefit plan terms.

4. TERM OF EMPLOYMENT
This Agreement shall commence on the effective date and continue until terminated by either party in accordance with the terms herein.

5. TERMINATION
Either party may terminate this Agreement upon 30 days written notice to the other party.

6. CONFIDENTIALITY
Employee shall maintain the confidentiality of all proprietary and confidential information of Employer.

IN WITNESS WHEREOF, the parties have executed this Agreement as of the date first above written.

{company1}                                    {company2}
By: ___________________________    By: ___________________________
Title: _________________________    Title: _________________________
Date: __________________________    Date: ___________________________
"""

def generate_vendor_content(template: Dict, company1: str, company2: str, start_date: datetime, end_date: datetime) -> str:
    """Generate Vendor contract content."""
    service = random.choice(template["services"])
    metric = random.choice(template["performance_metrics"])
    payment = random.choice(template["payment_terms"])
    
    return f"""
VENDOR AGREEMENT

This Vendor Agreement (the "Agreement") is entered into as of {start_date.strftime('%B %d, %Y')} by and between {company1}, a corporation organized under the laws of the State of California ("Client"), and {company2}, a corporation organized under the laws of the State of Delaware ("Vendor").

1. SERVICES
Vendor shall provide {service} to Client in accordance with the terms and conditions of this Agreement.

2. PERFORMANCE STANDARDS
Vendor shall maintain performance standards including {metric} and shall provide monthly performance reports.

3. PAYMENT TERMS
Client shall pay Vendor according to the payment schedule specified in Exhibit A. Standard payment terms are {payment}.

4. QUALITY ASSURANCE
Vendor shall implement quality control measures and maintain quality standards as specified in this Agreement.

5. LIABILITY
Vendor's liability shall be limited to the amount paid by Client under this Agreement in the 12 months preceding the claim.

6. TERMINATION
Either party may terminate this Agreement upon 60 days written notice to the other party.

IN WITNESS WHEREOF, the parties have executed this Agreement as of the date first above written.

{company1}                                    {company2}
By: ___________________________    By: ___________________________
Title: _________________________    Title: _________________________
Date: __________________________    Date: ___________________________
"""

def generate_lease_content(template: Dict, company1: str, company2: str, start_date: datetime, end_date: datetime) -> str:
    """Generate Lease contract content."""
    property_type = random.choice(template["property_types"])
    lease_term = random.choice(template["lease_terms"])
    utility = random.choice(template["utilities"])
    
    return f"""
LEASE AGREEMENT

This Lease Agreement (the "Lease") is entered into as of {start_date.strftime('%B %d, %Y')} by and between {company1}, a corporation organized under the laws of the State of California ("Landlord"), and {company2}, a corporation organized under the laws of the State of Delaware ("Tenant").

1. PREMISES
Landlord hereby leases to Tenant the {property_type} located at {random.randint(100, 9999)} Business Street, Suite {random.randint(1, 999)}, {random.choice(['San Francisco', 'New York', 'Los Angeles', 'Chicago', 'Austin'])}.

2. TERM
The term of this Lease shall be {lease_term} commencing on the effective date.

3. RENT
Tenant shall pay monthly rent of ${random.randint(1000, 10000):,} due on the first day of each month.

4. UTILITIES
Tenant shall be responsible for {utility} and other utilities as specified in this Lease.

5. MAINTENANCE
Landlord shall be responsible for structural repairs and major systems. Tenant shall be responsible for routine maintenance and cleaning.

6. USE
Tenant shall use the premises solely for business purposes and in compliance with all applicable laws and regulations.

7. TERMINATION
Either party may terminate this Lease upon 30 days written notice to the other party.

IN WITNESS WHEREOF, the parties have executed this Lease as of the date first above written.

{company1}                                    {company2}
By: ___________________________    By: ___________________________
Title: _________________________    Title: _________________________
Date: __________________________    Date: ___________________________
"""

def generate_other_content(template: Dict, company1: str, company2: str, start_date: datetime, end_date: datetime) -> str:
    """Generate Other contract content."""
    agreement_type = random.choice(template["agreement_types"])
    focus = random.choice(template["focus_areas"])
    
    return f"""
{agreement_type.upper()} AGREEMENT

This {agreement_type.title()} Agreement (the "Agreement") is entered into as of {start_date.strftime('%B %d, %Y')} by and between {company1}, a corporation organized under the laws of the State of California ("Party A"), and {company2}, a corporation organized under the laws of the State of Delaware ("Party B").

1. PURPOSE
The parties wish to establish a {agreement_type} relationship for {focus} purposes.

2. SCOPE OF COLLABORATION
The parties shall collaborate on {focus} initiatives as mutually agreed upon in writing.

3. TERM
This Agreement shall commence on the effective date and continue for {random.randint(1, 5)} years unless earlier terminated.

4. RESPONSIBILITIES
Each party shall be responsible for their respective obligations as outlined in this Agreement and any subsequent amendments.

5. CONFIDENTIALITY
Both parties shall maintain the confidentiality of any proprietary information shared during the course of this Agreement.

6. TERMINATION
Either party may terminate this Agreement upon 60 days written notice to the other party.

IN WITNESS WHEREOF, the parties have executed this Agreement as of the date first above written.

{company1}                                    {company2}
By: ___________________________    By: ___________________________
Title: _________________________    Title: _________________________
Date: __________________________    Date: ___________________________
"""

def main():
    """Main function to generate test contracts."""
    print("🚀 ContractGuard.ai - Test Contract Generator (Simplified)")
    print("=" * 60)
    
    # Set random seed for reproducibility
    random.seed(42)
    
    # Generate contracts for each category
    categories = ["NDA", "MSA", "SOW", "Employment", "Vendor", "Lease", "Other"]
    
    print(f"\n📄 Generating test contracts for {len(categories)} categories...")
    print("📁 Contracts will be saved to the 'test_contracts' directory")
    
    # Create output directory
    output_dir = "test_contracts"
    os.makedirs(output_dir, exist_ok=True)
    
    total_contracts = 0
    
    for category in categories:
        print(f"\n📄 Processing {category} contracts...")
        print("-" * 30)
        
        # Generate 2-3 contracts per category for variety
        num_contracts = random.randint(2, 3)
        
        for i in range(num_contracts):
            print(f"\n--- Contract {i+1}/{num_contracts} ---")
            
            # Generate contract content
            contract_data = generate_contract_content(category)
            print(f"📝 Generated: {contract_data['title']}")
            
            # Save contract to file
            filename = f"{output_dir}/{category}_{i+1}_{contract_data['counterparty'].replace(' ', '_')}.txt"
            with open(filename, 'w') as f:
                f.write(contract_data["content"])
            
            print(f"💾 Saved to: {filename}")
            total_contracts += 1
            
            # Small delay between contracts
            time.sleep(0.1)
    
    print(f"\n🎉 Test contract generation complete!")
    print(f"📊 Generated {total_contracts} contracts across all {len(categories)} categories")
    print(f"📁 All contracts saved to: {output_dir}/")
    print(f"\n🔍 Next steps:")
    print(f"   1. Upload these contracts through the ContractGuard.ai interface")
    print(f"   2. Run AI analysis on each contract")
    print(f"   3. Review the analysis results and risk assessments")
    print(f"   4. Use the results to train and improve the AI model")

if __name__ == "__main__":
    main()
