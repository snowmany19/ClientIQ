# backend/templates/ai/contract_analysis_prompts.py
# ContractGuard.ai - AI Prompt Templates

import json

# ===========================
# 📋 Contract Analysis Prompts
# ===========================

SUMMARY_PROMPT_TEMPLATE = """
You are an expert contract analyst. Create a comprehensive summary of this contract.

CONTRACT DETAILS:
Title: {title}
Counterparty: {counterparty}
Category: {category}
Effective Date: {effective_date}
Term End: {term_end}
Governing Law: {governing_law}

CONTRACT TEXT:
{contract_text}

Provide a JSON response with this structure:
{{
    "executive_summary": "2-3 paragraph high-level summary",
    "key_terms": {{
        "parties": "Identified parties and their roles",
        "scope": "Scope of work, services, or obligations",
        "payment": "Payment terms, amounts, and schedule",
        "term": "Contract duration and key dates",
        "termination": "Termination conditions and notice periods",
        "confidentiality": "Confidentiality and non-disclosure provisions",
        "intellectual_property": "IP ownership, licensing, and rights",
        "indemnity": "Indemnification clauses and scope",
        "liability": "Liability limitations and caps",
        "dispute_resolution": "Dispute resolution mechanism",
        "renewal": "Renewal terms and conditions",
        "assignment": "Assignment and transfer restrictions",
        "non_solicit": "Non-solicitation clauses",
        "non_compete": "Non-compete restrictions"
    }},
    "business_impact": "Analysis of business impact and implications",
    "critical_dates": ["List of important dates and deadlines"],
    "obligations": ["Key obligations for each party"]
}}

Focus on clarity, accuracy, and business relevance.
"""

RISK_ASSESSMENT_PROMPT_TEMPLATE = """
You are an expert contract risk analyst. Identify and assess risks in this contract.

CONTRACT DETAILS:
Title: {title}
Category: {category}
Counterparty: {counterparty}

FOCUS AREAS FOR {category_upper} CONTRACTS:
{focus_areas}

COMMON RISKS FOR {category_upper} CONTRACTS:
{common_risks}

CONTRACT TEXT:
{contract_text}

Identify risks and provide a JSON array with this structure:
[
    {{
        "severity": 1-5,  // 1=Low, 2=Medium-Low, 3=Medium, 4=High, 5=Critical
        "confidence": 0.0-1.0,  // Confidence in risk assessment
        "category": "risk category (e.g., liability, payment, termination)",
        "title": "Brief risk title",
        "description": "Detailed risk description",
        "rationale": "Why this is a risk and potential impact",
        "clause_reference": "Specific clause or section reference",
        "business_impact": "Potential business impact",
        "mitigation_suggestions": ["List of potential mitigations"]
    }}
]

Focus on:
1. Unfavorable terms that could harm the company
2. Missing protections or clauses
3. Unclear or ambiguous language
4. Unreasonable obligations or restrictions
5. Regulatory or compliance risks
6. Financial risks
7. Operational risks

Rate severity from 1 (low) to 5 (critical) with confidence scores.
"""

REWRITE_SUGGESTIONS_PROMPT_TEMPLATE = """
You are an expert contract negotiator. Provide rewrite suggestions for problematic contract clauses.

CONTRACT DETAILS:
Title: {title}
Category: {category}
Counterparty: {counterparty}

IDENTIFIED HIGH-RISK ISSUES:
{high_risk_issues}

CONTRACT TEXT:
{contract_text}

For each high-risk issue, provide rewrite suggestions in this JSON structure:
[
    {{
        "risk_id": "Reference to the risk being addressed",
        "type": "balanced|company_favorable",
        "category": "suggestion category",
        "original_text": "Original problematic text (if identifiable)",
        "suggested_text": "Improved clause language",
        "rationale": "Why this change is recommended",
        "negotiation_tips": ["Tips for negotiating this change"],
        "fallback_position": "Alternative position if primary suggestion is rejected"
    }}
]

Provide both:
1. BALANCED suggestions that are fair to both parties
2. COMPANY-FAVORABLE suggestions that protect your company's interests

Focus on:
- Clearer language and definitions
- Balanced obligations and rights
- Reasonable limitations and protections
- Industry-standard terms
- Regulatory compliance
"""

CATEGORY_ANALYSIS_PROMPT_TEMPLATE = """
You are an expert in {category} contracts. Perform a category-specific analysis.

CONTRACT DETAILS:
Title: {title}
Category: {category}
Counterparty: {counterparty}

FOCUS AREAS FOR {category_upper} CONTRACTS:
{focus_areas}

CONTRACT TEXT:
{contract_text}

Provide a JSON response with category-specific analysis:
{{
    "category_insights": "Specific insights for {category} contracts",
    "industry_standards": "How this contract compares to industry standards",
    "missing_elements": ["Standard elements that are missing"],
    "unusual_provisions": ["Unusual or non-standard provisions"],
    "regulatory_considerations": ["Regulatory issues to consider"],
    "best_practices": ["Best practices for {category} contracts"],
    "red_flags": ["Specific red flags for this contract type"]
}}

Focus on {category}-specific considerations and industry standards.
"""

COMPLIANCE_CHECK_PROMPT_TEMPLATE = """
You are a compliance expert. Check this contract for compliance and regulatory issues.

CONTRACT DETAILS:
Title: {title}
Category: {category}
Governing Law: {governing_law}

CONTRACT TEXT:
{contract_text}

Provide a JSON response with compliance analysis:
{{
    "regulatory_risks": [
        {{
            "regulation": "Specific regulation or law",
            "issue": "Compliance issue description",
            "severity": "high|medium|low",
            "recommendation": "How to address the issue"
        }}
    ],
    "data_privacy": "Data privacy and GDPR considerations",
    "employment_law": "Employment law considerations (if applicable)",
    "intellectual_property": "IP law considerations",
    "tax_implications": "Tax implications and considerations",
    "industry_regulations": "Industry-specific regulations to consider",
    "compliance_recommendations": ["List of compliance recommendations"]
}}

Focus on:
- Data protection and privacy laws
- Employment regulations (if applicable)
- Industry-specific regulations
- Tax implications
- Intellectual property laws
- Anti-corruption and bribery laws
"""

CONTRACT_QA_PROMPT_TEMPLATE = """
You are an expert contract analyst. Answer this specific question about the contract.

CONTRACT DETAILS:
Title: {title}
Category: {category}
Counterparty: {counterparty}

CONTRACT TEXT:
{contract_text}

QUESTION: {question}

Provide a JSON response:
{{
    "answer": "Direct answer to the question",
    "confidence": 0.0-1.0,  // Confidence in the answer
    "source_reference": "Specific clause or section reference",
    "context": "Additional context and explanation",
    "implications": "Business implications of the answer",
    "recommendations": ["Related recommendations"]
}}

IMPORTANT: Base your answer ONLY on the contract text provided. Do not make assumptions or reference external information.
"""

# ===========================
# 🎯 Category-Specific Prompts
# ===========================

NDA_SPECIFIC_PROMPT = """
For NDA contracts, pay special attention to:
- Definition of confidential information
- Term and survival periods
- Permitted disclosures and carve-outs
- Return/destruction obligations
- Remedies for breach
- Non-solicitation provisions
"""

MSA_SPECIFIC_PROMPT = """
For MSA contracts, pay special attention to:
- Scope of services and deliverables
- Payment terms and schedules
- Performance standards and SLAs
- Change management procedures
- Liability limitations and caps
- Indemnification provisions
- Termination rights and notice periods
"""

SOW_SPECIFIC_PROMPT = """
For SOW contracts, pay special attention to:
- Detailed deliverables and acceptance criteria
- Project timeline and milestones
- Payment schedule tied to deliverables
- Change order procedures
- Intellectual property ownership
- Warranty and support terms
"""

EMPLOYMENT_SPECIFIC_PROMPT = """
For Employment contracts, pay special attention to:
- Compensation and benefits
- Job duties and responsibilities
- Termination provisions
- Non-compete and non-solicitation clauses
- Intellectual property assignment
- Confidentiality obligations
- Dispute resolution procedures
"""

VENDOR_SPECIFIC_PROMPT = """
For Vendor contracts, pay special attention to:
- Service level agreements
- Performance guarantees
- Payment terms and penalties
- Liability limitations
- Insurance requirements
- Termination and transition
- Data security and privacy
"""

LEASE_SPECIFIC_PROMPT = """
For Lease contracts, pay special attention to:
- Rent amount and escalation clauses
- Term and renewal options
- Maintenance and repair obligations
- Utilities and operating expenses
- Use restrictions and compliance
- Assignment and subletting rights
- Default and termination provisions
"""

# ===========================
# 🔧 Prompt Utility Functions
# ===========================

def format_summary_prompt(contract, contract_text):
    """Format the summary prompt with contract details."""
    return SUMMARY_PROMPT_TEMPLATE.format(
        title=contract.title,
        counterparty=contract.counterparty,
        category=contract.category,
        effective_date=contract.effective_date or "Not specified",
        term_end=contract.term_end or "Not specified",
        governing_law=contract.governing_law or "Not specified",
        contract_text=contract_text[:6000]
    )

def format_risk_assessment_prompt(contract, contract_text, category_info):
    """Format the risk assessment prompt with contract details."""
    return RISK_ASSESSMENT_PROMPT_TEMPLATE.format(
        title=contract.title,
        category=contract.category,
        category_upper=contract.category.upper(),
        counterparty=contract.counterparty,
        focus_areas=", ".join(category_info.get("focus_areas", [])),
        common_risks=", ".join(category_info.get("risks", [])),
        contract_text=contract_text[:6000]
    )

def format_rewrite_suggestions_prompt(contract, contract_text, high_risk_issues):
    """Format the rewrite suggestions prompt."""
    return REWRITE_SUGGESTIONS_PROMPT_TEMPLATE.format(
        title=contract.title,
        category=contract.category,
        counterparty=contract.counterparty,
        high_risk_issues=json.dumps(high_risk_issues, indent=2),
        contract_text=contract_text[:6000]
    )

def format_category_analysis_prompt(contract, contract_text, category_info):
    """Format the category analysis prompt."""
    return CATEGORY_ANALYSIS_PROMPT_TEMPLATE.format(
        title=contract.title,
        category=contract.category,
        category_upper=contract.category.upper(),
        counterparty=contract.counterparty,
        focus_areas=", ".join(category_info.get("focus_areas", [])),
        contract_text=contract_text[:6000]
    )

def format_compliance_check_prompt(contract, contract_text):
    """Format the compliance check prompt."""
    return COMPLIANCE_CHECK_PROMPT_TEMPLATE.format(
        title=contract.title,
        category=contract.category,
        governing_law=contract.governing_law or "Not specified",
        contract_text=contract_text[:6000]
    )

def format_contract_qa_prompt(contract, contract_text, question):
    """Format the contract Q&A prompt."""
    return CONTRACT_QA_PROMPT_TEMPLATE.format(
        title=contract.title,
        category=contract.category,
        counterparty=contract.counterparty,
        contract_text=contract_text[:8000],
        question=question
    )

def get_category_specific_prompt(category):
    """Get category-specific prompt additions."""
    category_prompts = {
        "NDA": NDA_SPECIFIC_PROMPT,
        "MSA": MSA_SPECIFIC_PROMPT,
        "SOW": SOW_SPECIFIC_PROMPT,
        "Employment": EMPLOYMENT_SPECIFIC_PROMPT,
        "Vendor": VENDOR_SPECIFIC_PROMPT,
        "Lease": LEASE_SPECIFIC_PROMPT
    }
    return category_prompts.get(category, "")
