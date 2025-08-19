# backend/utils/contract_analyzer.py
# ContractGuard.ai - Advanced Contract Analysis

import os
import json
import re
from typing import Dict, List, Any, Optional
from datetime import datetime
from openai import OpenAI
from sqlalchemy.orm import Session

from core.config import get_settings
from utils.logger import get_logger
from models import ContractRecord
from templates.ai.contract_analysis_prompts import (
    format_summary_prompt, format_risk_assessment_prompt, 
    format_rewrite_suggestions_prompt, format_category_analysis_prompt,
    format_compliance_check_prompt, format_contract_qa_prompt,
    get_category_specific_prompt
)

settings = get_settings()
logger = get_logger("contract_analyzer")

# Initialize OpenAI client
client = OpenAI(api_key=settings.openai_api_key)

# Contract categories and their specific analysis focus
CONTRACT_CATEGORIES = {
    "NDA": {
        "focus_areas": ["confidentiality", "non-disclosure", "term", "survival", "exclusions"],
        "risks": ["overly broad confidentiality", "unlimited term", "no carve-outs", "one-sided obligations"]
    },
    "MSA": {
        "focus_areas": ["scope", "payment", "term", "termination", "liability", "indemnity"],
        "risks": ["unlimited liability", "auto-renewal", "unfavorable payment terms", "broad indemnity"]
    },
    "SOW": {
        "focus_areas": ["deliverables", "timeline", "payment", "acceptance", "change_management"],
        "risks": ["vague deliverables", "unrealistic timelines", "late payment penalties", "scope creep"]
    },
    "Employment": {
        "focus_areas": ["compensation", "benefits", "termination", "non-compete", "ip_ownership"],
        "risks": ["unfavorable termination", "overly broad non-compete", "unclear ip ownership"]
    },
    "Vendor": {
        "focus_areas": ["services", "payment", "performance", "liability", "termination"],
        "risks": ["unlimited liability", "unfavorable payment terms", "no performance guarantees"]
    },
    "Lease": {
        "focus_areas": ["term", "rent", "maintenance", "utilities", "termination", "renewal"],
        "risks": ["auto-renewal", "unfavorable maintenance obligations", "rent increases"]
    },
    "Other": {
        "focus_areas": ["general_terms", "obligations", "liability", "termination"],
        "risks": ["unfavorable terms", "unclear obligations", "unlimited liability"]
    }
}

async def analyze_contract_comprehensive(contract: ContractRecord, db: Session) -> Dict[str, Any]:
    """
    Perform comprehensive contract analysis using multiple AI passes.
    """
    try:
        # Extract text from uploaded files
        contract_text = await extract_contract_text(contract)
        if not contract_text.strip():
            raise Exception("No text content found in uploaded files")
        
        # Perform multi-pass analysis
        analysis_results = {}
        
        # Pass 1: Basic summary and key terms extraction
        analysis_results["summary"] = await generate_contract_summary(contract, contract_text)
        
        # Pass 2: Risk assessment
        analysis_results["risks"] = await assess_contract_risks(contract, contract_text)
        
        # Pass 3: Rewrite suggestions
        analysis_results["suggestions"] = await generate_rewrite_suggestions(contract, contract_text, analysis_results["risks"])
        
        # Pass 4: Category-specific analysis
        analysis_results["category_analysis"] = await perform_category_analysis(contract, contract_text)
        
        # Pass 5: Compliance check
        analysis_results["compliance"] = await check_compliance_issues(contract, contract_text)
        
        return {
            "analysis_json": analysis_results,
            "summary": analysis_results["summary"]["executive_summary"],
            "risks": analysis_results["risks"],
            "suggestions": analysis_results["suggestions"]
        }
        
    except Exception as e:
        logger.error(f"Comprehensive contract analysis failed: {e}")
        return {
            "analysis_json": {},
            "summary": "Analysis failed. Please try again or contact support.",
            "risks": [],
            "suggestions": []
        }

async def extract_contract_text(contract: ContractRecord) -> str:
    """Extract text from uploaded contract files."""
    contract_text = ""
    
    for file_path in contract.uploaded_files or []:
        # Handle both relative and absolute paths
        if not os.path.isabs(file_path):
            # If it's a relative path, make it relative to the backend directory
            backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            full_path = os.path.join(backend_dir, file_path)
        else:
            full_path = file_path
            
        if os.path.exists(full_path):
            file_extension = os.path.splitext(full_path)[1].lower()
            
            try:
                if file_extension == '.pdf':
                    # Extract text from PDF
                    import PyPDF2
                    with open(full_path, 'rb') as file:
                        pdf_reader = PyPDF2.PdfReader(file)
                        for page in pdf_reader.pages:
                            contract_text += page.extract_text() + "\n"
                            
                elif file_extension in ['.txt']:
                    # Read text file
                    with open(full_path, 'r', encoding='utf-8') as file:
                        contract_text += file.read() + "\n"
                        
                elif file_extension in ['.docx']:
                    # Extract text from DOCX (basic implementation)
                    try:
                        import docx
                        doc = docx.Document(full_path)
                        for paragraph in doc.paragraphs:
                            contract_text += paragraph.text + "\n"
                    except ImportError:
                        logger.warning("python-docx not installed, skipping DOCX file")
                        
            except Exception as e:
                logger.warning(f"Failed to extract text from {full_path}: {e}")
                continue
        else:
            logger.warning(f"File not found: {full_path}")
    
    return contract_text

async def generate_contract_summary(contract: ContractRecord, contract_text: str) -> Dict[str, Any]:
    """Generate comprehensive contract summary."""
    
    try:
        # Use template to format prompt
        prompt = format_summary_prompt(contract, contract_text)
        
        # Add category-specific guidance
        category_prompt = get_category_specific_prompt(contract.category)
        if category_prompt:
            prompt += f"\n\n{category_prompt}"
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2
        )
        
        content = response.choices[0].message.content
        if content is None:
            raise Exception("Empty response from GPT")
        
        # Try to parse JSON, with fallback handling
        try:
            return json.loads(content)
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse JSON response: {e}. Content: {content[:200]}...")
            # Try to extract JSON from the response if it's wrapped in markdown
            import re
            
            # First try to extract content between ```json and ``` markers
            json_block_match = re.search(r'```json\s*(.*?)\s*```', content, re.DOTALL)
            if json_block_match:
                try:
                    return json.loads(json_block_match.group(1).strip())
                except json.JSONDecodeError:
                    logger.warning("Failed to parse JSON from markdown block")
            
            # Fallback: try to extract JSON object from the content
            json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', content, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group())
                except json.JSONDecodeError:
                    logger.error(f"Could not extract valid JSON from response")
                    return {
                        "executive_summary": "Unable to generate summary due to technical issues.",
                        "key_terms": {},
                        "business_impact": "Analysis unavailable.",
                        "critical_dates": [],
                        "obligations": []
                    }
            else:
                logger.error(f"No JSON object found in response")
                return {
                    "executive_summary": "Unable to generate summary due to technical issues.",
                    "key_terms": {},
                    "business_impact": "Analysis unavailable.",
                    "critical_dates": [],
                    "obligations": []
                }
        
    except Exception as e:
        logger.error(f"Summary generation failed: {e}")
        return {
            "executive_summary": "Unable to generate summary due to technical issues.",
            "key_terms": {},
            "business_impact": "Analysis unavailable.",
            "critical_dates": [],
            "obligations": []
        }

async def assess_contract_risks(contract: ContractRecord, contract_text: str) -> List[Dict[str, Any]]:
    """Assess contract risks with detailed analysis."""
    
    try:
        category_focus = CONTRACT_CATEGORIES.get(contract.category, CONTRACT_CATEGORIES["Other"])
        
        # Use template to format prompt
        prompt = format_risk_assessment_prompt(contract, contract_text, category_focus)
        
        # Add category-specific guidance
        category_prompt = get_category_specific_prompt(contract.category)
        if category_prompt:
            prompt += f"\n\n{category_prompt}"
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        
        content = response.choices[0].message.content
        if content is None:
            raise Exception("Empty response from GPT")
        
        # Try to parse JSON, with fallback handling
        try:
            risks = json.loads(content)
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse JSON response: {e}. Content: {content[:200]}...")
            # Try to extract JSON from the response if it's wrapped in markdown
            import re
            
            # First try to extract content between ```json and ``` markers
            json_block_match = re.search(r'```json\s*(.*?)\s*```', content, re.DOTALL)
            if json_block_match:
                try:
                    risks = json.loads(json_block_match.group(1).strip())
                    if isinstance(risks, list):
                        return risks
                except json.JSONDecodeError:
                    logger.warning("Failed to parse JSON from markdown block")
            
            # Fallback: try to extract JSON array from the content
            json_match = re.search(r'\[[^\[\]]*(?:\{[^{}]*\}[^\[\]]*)*\]', content, re.DOTALL)
            if json_match:
                try:
                    risks = json.loads(json_match.group())
                    if isinstance(risks, list):
                        return risks
                except json.JSONDecodeError:
                    logger.error(f"Could not extract valid JSON from response")
                    return []
            else:
                logger.error(f"No JSON array found in response")
                return []
        
        # Validate and clean risks
        validated_risks = []
        for risk in risks:
            if isinstance(risk, dict) and "severity" in risk:
                # Ensure severity is within bounds
                risk["severity"] = max(1, min(5, risk.get("severity", 3)))
                risk["confidence"] = max(0.0, min(1.0, risk.get("confidence", 0.5)))
                validated_risks.append(risk)
        
        return validated_risks
        
    except Exception as e:
        logger.error(f"Risk assessment failed: {e}")
        return []

async def generate_rewrite_suggestions(contract: ContractRecord, contract_text: str, risks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Generate rewrite suggestions based on identified risks."""
    
    if not risks:
        return []
    
    # Focus on high-severity risks for rewrite suggestions
    high_risk_issues = [risk for risk in risks if risk.get("severity", 0) >= 4]
    
    if not high_risk_issues:
        return []
    
    prompt = f"""
You are an expert contract negotiator. Provide rewrite suggestions for problematic contract clauses.

CONTRACT DETAILS:
Title: {contract.title}
Category: {contract.category}
Counterparty: {contract.counterparty}

IDENTIFIED HIGH-RISK ISSUES:
{json.dumps(high_risk_issues, indent=2)}

CONTRACT TEXT:
{contract_text[:6000]}

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

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4
        )
        
        content = response.choices[0].message.content
        if content is None:
            raise Exception("Empty response from GPT")
        
        # Try to parse JSON, with fallback handling
        try:
            suggestions = json.loads(content)
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse JSON response: {e}. Content: {content[:200]}...")
            # Try to extract JSON from the response if it's wrapped in text
            import re
            json_match = re.search(r'\[.*\]', content, re.DOTALL)
            if json_match:
                try:
                    suggestions = json.loads(json_match.group())
                except json.JSONDecodeError:
                    logger.error(f"Could not extract valid JSON from response")
                    return []
            else:
                logger.error(f"No JSON array found in response")
                return []
        
        # Validate suggestions
        validated_suggestions = []
        for suggestion in suggestions:
            if isinstance(suggestion, dict) and "suggested_text" in suggestion:
                validated_suggestions.append(suggestion)
        
        return validated_suggestions
        
    except Exception as e:
        logger.error(f"Rewrite suggestions failed: {e}")
        return []

async def perform_category_analysis(contract: ContractRecord, contract_text: str) -> Dict[str, Any]:
    """Perform category-specific analysis based on contract type."""
    
    category = contract.category
    if category not in CONTRACT_CATEGORIES:
        category = "Other"
    
    category_info = CONTRACT_CATEGORIES[category]
    
    prompt = f"""
You are an expert in {category} contracts. Perform a category-specific analysis.

CONTRACT DETAILS:
Title: {contract.title}
Category: {category}
Counterparty: {contract.counterparty}

FOCUS AREAS FOR {category.upper()} CONTRACTS:
{', '.join(category_info['focus_areas'])}

CONTRACT TEXT:
{contract_text[:6000]}

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

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        
        content = response.choices[0].message.content
        if content is None:
            raise Exception("Empty response from GPT")
        
        # Try to parse JSON, with fallback handling
        try:
            return json.loads(content)
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse JSON response: {e}. Content: {content[:200]}...")
            # Try to extract JSON from the response if it's wrapped in markdown
            import re
            
            # First try to extract content between ```json and ``` markers
            json_block_match = re.search(r'```json\s*(.*?)\s*```', content, re.DOTALL)
            if json_block_match:
                try:
                    return json.loads(json_block_match.group(1).strip())
                except json.JSONDecodeError:
                    logger.warning("Failed to parse JSON from markdown block")
            
            # Fallback: try to extract JSON object from the content
            json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', content, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group())
                except json.JSONDecodeError:
                    logger.error(f"Could not extract valid JSON from response")
                    return {
                        "category_insights": "Category-specific analysis unavailable.",
                        "industry_standards": "Unable to compare to industry standards.",
                        "missing_elements": [],
                        "unusual_provisions": [],
                        "regulatory_considerations": [],
                        "best_practices": [],
                        "red_flags": []
                    }
            else:
                logger.error(f"No JSON object found in response")
                return {
                    "category_insights": "Category-specific analysis unavailable.",
                    "industry_standards": "Unable to compare to industry standards.",
                    "missing_elements": [],
                    "unusual_provisions": [],
                    "regulatory_considerations": [],
                    "best_practices": [],
                    "red_flags": []
                }
        
    except Exception as e:
        logger.error(f"Category analysis failed: {e}")
        return {
            "category_insights": "Category-specific analysis unavailable.",
            "industry_standards": "Unable to compare to industry standards.",
            "missing_elements": [],
            "unusual_provisions": [],
            "regulatory_considerations": [],
            "best_practices": [],
            "red_flags": []
        }

async def check_compliance_issues(contract: ContractRecord, contract_text: str) -> Dict[str, Any]:
    """Check for compliance and regulatory issues."""
    
    prompt = f"""
You are a compliance expert. Check this contract for compliance and regulatory issues.

CONTRACT DETAILS:
Title: {contract.title}
Category: {contract.category}
Governing Law: {contract.governing_law}

CONTRACT TEXT:
{contract_text[:6000]}

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

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2
        )
        
        content = response.choices[0].message.content
        if content is None:
            raise Exception("Empty response from GPT")
        
        # Try to parse JSON, with fallback handling
        try:
            return json.loads(content)
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse JSON response: {e}. Content: {content[:200]}...")
            # Try to extract JSON from the response if it's wrapped in markdown
            import re
            
            # First try to extract content between ```json and ``` markers
            json_block_match = re.search(r'```json\s*(.*?)\s*```', content, re.DOTALL)
            if json_block_match:
                try:
                    return json.loads(json_block_match.group(1).strip())
                except json.JSONDecodeError:
                    logger.warning("Failed to parse JSON from markdown block")
            
            # Fallback: try to extract JSON object from the content
            json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', content, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group())
                except json.JSONDecodeError:
                    logger.error(f"Could not extract valid JSON from response")
                    return {
                        "regulatory_risks": [],
                        "data_privacy": "Compliance analysis unavailable.",
                        "employment_law": "Employment law analysis unavailable.",
                        "intellectual_property": "IP law analysis unavailable.",
                        "tax_implications": "Tax analysis unavailable.",
                        "industry_regulations": "Industry regulation analysis unavailable.",
                        "compliance_recommendations": []
                    }
            else:
                logger.error(f"No JSON object found in response")
                return {
                    "regulatory_risks": [],
                    "data_privacy": "Compliance analysis unavailable.",
                    "employment_law": "Employment law analysis unavailable.",
                    "intellectual_property": "IP law analysis unavailable.",
                    "tax_implications": "Tax analysis unavailable.",
                    "industry_regulations": "Industry regulation analysis unavailable.",
                    "compliance_recommendations": []
                }
        
    except Exception as e:
        logger.error(f"Compliance check failed: {e}")
        return {
            "regulatory_risks": [],
            "data_privacy": "Compliance analysis unavailable.",
            "employment_law": "Employment law analysis unavailable.",
            "intellectual_property": "IP law analysis unavailable.",
            "tax_implications": "Tax analysis unavailable.",
            "industry_regulations": "Industry regulation analysis unavailable.",
            "compliance_recommendations": []
        }

async def answer_contract_question(contract: ContractRecord, question: str, db: Session) -> Dict[str, Any]:
    """Answer specific questions about the contract using AI."""
    
    try:
        # Extract contract text
        contract_text = await extract_contract_text(contract)
        if not contract_text.strip():
            raise Exception("No text content found in uploaded files")
        
        prompt = f"""
You are an expert contract analyst. Answer this specific question about the contract.

CONTRACT DETAILS:
Title: {contract.title}
Category: {contract.category}
Counterparty: {contract.counterparty}

CONTRACT TEXT:
{contract_text[:8000]}

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

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2
        )
        
        content = response.choices[0].message.content
        if content is None:
            raise Exception("Empty response from GPT")
        
        # Try to parse JSON, with fallback handling
        try:
            return json.loads(content)
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse JSON response: {e}. Content: {content[:200]}...")
            # Try to extract JSON from the response if it's wrapped in markdown
            import re
            
            # First try to extract content between ```json and ``` markers
            json_block_match = re.search(r'```json\s*(.*?)\s*```', content, re.DOTALL)
            if json_block_match:
                try:
                    return json.loads(json_block_match.group(1).strip())
                except json.JSONDecodeError:
                    logger.warning("Failed to parse JSON from markdown block")
            
            # Fallback: try to extract JSON object from the content
            json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', content, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group())
                except json.JSONDecodeError:
                    logger.error(f"Could not extract valid JSON from response")
                    return {
                        "answer": "Unable to answer the question due to technical issues.",
                        "confidence": 0.0,
                        "source_reference": "N/A",
                        "context": "Analysis unavailable.",
                        "implications": "Unable to assess implications.",
                        "recommendations": []
                    }
            else:
                logger.error(f"No JSON object found in response")
                return {
                    "answer": "Unable to answer the question due to technical issues.",
                    "confidence": 0.0,
                    "source_reference": "N/A",
                    "context": "Analysis unavailable.",
                    "implications": "Unable to assess implications.",
                    "recommendations": []
                }
        
    except Exception as e:
        logger.error(f"Contract Q&A failed: {e}")
        return {
            "answer": "Unable to answer the question due to technical issues.",
            "confidence": 0.0,
            "source_reference": "N/A",
            "context": "Analysis unavailable.",
            "implications": "Unable to assess implications.",
            "recommendations": []
        }
