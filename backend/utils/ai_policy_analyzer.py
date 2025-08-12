# backend/utils/ai_policy_analyzer.py
# AI-powered contract analysis for ContractGuard.ai

import os
import json
import logging
from typing import Dict, Any, List, Optional
from openai import OpenAI
from utils.logger import get_logger

logger = get_logger("ai_policy_analyzer")

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def analyze_contract_policy(contract_content: str, contract_type: str = "general") -> Dict[str, Any]:
    """
    Analyze contract content using AI to extract key information.
    
    Args:
        contract_content: The contract text content
        contract_type: Type of contract (NDA, MSA, SOW, Employment, Vendor, Lease, Other)
        
    Returns:
        Structured analysis of the contract
    """
    try:
        # Create analysis prompt based on contract type
        prompt = f"""
        Analyze this {contract_type} contract document and extract the following information:
        
        CONTRACT CONTENT:
        {contract_content[:4000]}
        
        Please provide a structured analysis including:
        1. Key Terms and Conditions
        2. Obligations and Responsibilities
        3. Payment Terms and Schedules
        4. Termination Clauses
        5. Liability and Indemnification
        6. Governing Law and Jurisdiction
        7. Risk Assessment (High/Medium/Low)
        8. Compliance Requirements
        9. Critical Dates and Deadlines
        10. Recommendations for Review
        
        Format the response as JSON with clear sections.
        """
        
        # Get AI analysis
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert at analyzing contract documents and extracting structured information."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            max_tokens=2000
        )
        
        # Parse response
        analysis_text = response.choices[0].message.content
        
        # Try to extract JSON if present
        try:
            # Look for JSON in the response
            start_idx = analysis_text.find('{')
            end_idx = analysis_text.rfind('}') + 1
            if start_idx != -1 and end_idx != 0:
                json_str = analysis_text[start_idx:end_idx]
                analysis_data = json.loads(json_str)
            else:
                # If no JSON found, create structured response
                analysis_data = {
                    "analysis": analysis_text,
                    "contract_type": contract_type,
                    "extracted_terms": [],
                    "risk_level": "medium",
                    "compliance_status": "pending_review"
                }
        except json.JSONDecodeError:
            # Fallback to structured text response
            analysis_data = {
                "analysis": analysis_text,
                "contract_type": contract_type,
                "extracted_terms": [],
                "risk_level": "medium",
                "compliance_status": "pending_review"
            }
        
        logger.info(f"Contract analysis completed for {contract_type} contract")
        return analysis_data
        
    except Exception as e:
        logger.error(f"Contract analysis failed: {e}")
        return {
            "error": str(e),
            "contract_type": contract_type,
            "analysis": "Analysis failed due to technical error"
        }

async def generate_contract_specific_prompt(workspace_id: int, contract_content: str) -> str:
    """
    Generate a workspace-specific prompt for contract analysis.
    
    Args:
        workspace_id: The workspace ID
        contract_content: The contract content to base the prompt on
        
    Returns:
        Customized prompt for this workspace
    """
    prompt = f"""
    You are an AI assistant for workspace {workspace_id} contract management.
    
    CONTRACT CONTEXT:
    {contract_content[:2000]}
    
    When analyzing contracts for this workspace, please:
    1. Reference the specific industry standards and regulations
    2. Use the contract types and categories defined in their system
    3. Apply the risk levels and assessment criteria as specified
    4. Maintain consistency with their review procedures
    5. Use language and terminology that matches their business context
    
    Always prioritize the workspace's specific requirements over general guidelines.
    """
    
    return prompt

async def analyze_contracts_batch(contracts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Analyze multiple contracts in batch for efficiency.
    
    Args:
        contracts: List of contract data dictionaries
        
    Returns:
        List of analysis results
    """
    try:
        results = []
        
        for contract in contracts:
            # Analyze each contract
            analysis = await analyze_contract_policy(
                contract.get("content", ""),
                contract.get("type", "general")
            )
            
            # Add contract metadata
            analysis["contract_id"] = contract.get("id")
            analysis["contract_title"] = contract.get("title")
            analysis["analysis_timestamp"] = contract.get("timestamp")
            
            results.append(analysis)
        
        logger.info(f"Batch analysis completed for {len(contracts)} contracts")
        return results
        
    except Exception as e:
        logger.error(f"Batch contract analysis failed: {e}")
        return []

async def generate_contract_summary(contract_content: str, max_length: int = 500) -> str:
    """
    Generate a concise summary of contract content.
    
    Args:
        contract_content: The contract text content
        max_length: Maximum length of summary
        
    Returns:
        Concise contract summary
    """
    try:
        prompt = f"""
        Please provide a concise summary of the following contract document in {max_length} characters or less:
        
        {contract_content[:3000]}
        
        Focus on:
        - Main purpose and scope
        - Key parties involved
        - Primary obligations
        - Critical terms
        - Risk factors
        
        Provide a clear, business-friendly summary.
        """
        
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert at summarizing legal documents in clear, concise language."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            max_tokens=300
        )
        
        summary = response.choices[0].message.content.strip()
        
        # Ensure summary meets length requirement
        if len(summary) > max_length:
            summary = summary[:max_length-3] + "..."
        
        logger.info("Contract summary generated successfully")
        return summary
        
    except Exception as e:
        logger.error(f"Contract summary generation failed: {e}")
        return "Summary generation failed due to technical error."

async def extract_contract_risks(contract_content: str) -> List[Dict[str, Any]]:
    """
    Extract and categorize risks from contract content.
    
    Args:
        contract_content: The contract text content
        
    Returns:
        List of identified risks with details
    """
    try:
        prompt = """
        Analyze the following contract and identify potential risks:
        
        {contract_content}
        
        For each risk, provide:
        1. Risk Category (Legal, Financial, Operational, Compliance, etc.)
        2. Risk Level (High/Medium/Low)
        3. Risk Description
        4. Potential Impact
        5. Mitigation Suggestions
        
        Format as a structured list of risks.
        """
        
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert at identifying and analyzing contract risks."},
                {"role": "user", "content": prompt.format(contract_content=contract_content[:3000])}
            ],
            temperature=0.1,
            max_tokens=1500
        )
        
        risks_text = response.choices[0].message.content
        
        # Parse risks into structured format
        risks = []
        current_risk = {}
        
        for line in risks_text.split('\n'):
            line = line.strip()
            if line.startswith('Risk'):
                if current_risk:
                    risks.append(current_risk)
                current_risk = {}
            elif ':' in line:
                key, value = line.split(':', 1)
                current_risk[key.strip().lower().replace(' ', '_')] = value.strip()
        
        if current_risk:
            risks.append(current_risk)
        
        logger.info(f"Extracted {len(risks)} risks from contract")
        return risks
        
    except Exception as e:
        logger.error(f"Risk extraction failed: {e}")
        return []

async def generate_contract_recommendations(contract_analysis: Dict[str, Any]) -> List[str]:
    """
    Generate actionable recommendations based on contract analysis.
    
    Args:
        contract_analysis: The contract analysis results
        
    Returns:
        List of actionable recommendations
    """
    try:
        # Create recommendations based on analysis
        recommendations = []
        
        # Check for high-risk items
        if contract_analysis.get("risk_level") == "high":
            recommendations.append("Immediate legal review required due to high-risk factors")
            recommendations.append("Consider negotiating key terms before proceeding")
        
        # Check for missing critical elements
        if not contract_analysis.get("termination_clauses"):
            recommendations.append("Add clear termination clauses and notice periods")
        
        if not contract_analysis.get("liability_limits"):
            recommendations.append("Define liability limits and indemnification terms")
        
        # Check for compliance issues
        if contract_analysis.get("compliance_status") == "issues_found":
            recommendations.append("Address compliance issues before contract execution")
        
        # Add general recommendations
        recommendations.append("Ensure all parties have reviewed and approved the contract")
        recommendations.append("Set up monitoring for key dates and obligations")
        recommendations.append("Establish regular contract review schedule")
        
        logger.info(f"Generated {len(recommendations)} contract recommendations")
        return recommendations
        
    except Exception as e:
        logger.error(f"Recommendation generation failed: {e}")
        return ["Review contract with legal counsel", "Ensure compliance with company policies"] 