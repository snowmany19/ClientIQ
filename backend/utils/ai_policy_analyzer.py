# backend/utils/ai_policy_analyzer.py

import openai
import PyPDF2
import io
import json
from typing import Dict, List, Any, Optional
from core.config import get_settings

settings = get_settings()
openai.api_key = settings.openai_api_key

async def analyze_policy_document(pdf_content: bytes) -> Dict[str, Any]:
    """
    Analyze a policy document and extract structured information.
    
    Args:
        pdf_content: Raw PDF content as bytes
        
    Returns:
        Dictionary containing extracted policy information
    """
    try:
        # Extract text from PDF
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_content))
        full_text = ""
        for page in pdf_reader.pages:
            full_text += page.extract_text() + "\n"
        
        # Use OpenAI to analyze the policy document
        prompt = f"""
        Analyze this HOA policy document and extract the following information:
        
        DOCUMENT TEXT:
        {full_text[:4000]}  # Limit to first 4000 chars for API efficiency
        
        Please provide a JSON response with the following structure:
        {{
            "policy_name": "Name of the policy document",
            "effective_date": "When this policy takes effect",
            "categories": [
                {{
                    "name": "Category name (e.g., Parking, Landscaping, Noise)",
                    "rules": [
                        {{
                            "rule": "Specific rule description",
                            "severity": "low/medium/high",
                            "penalties": ["First warning", "Second warning", "Fine amount"]
                        }}
                    ]
                }}
            ],
            "violation_types": [
                "List of specific violation types found in the policy"
            ],
            "tags": [
                "List of relevant tags for categorizing violations"
            ],
            "summary": "Brief summary of the policy's main focus areas"
        }}
        
        Focus on extracting specific rules, violation types, and enforcement procedures.
        """
        
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert at analyzing HOA policy documents and extracting structured information."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        
        # Parse the JSON response
        analysis_result = json.loads(response.choices[0].message.content)
        
        return {
            "full_text": full_text,
            "ai_analysis": analysis_result,
            "extracted_categories": analysis_result.get("categories", []),
            "violation_types": analysis_result.get("violation_types", []),
            "tags": analysis_result.get("tags", []),
            "summary": analysis_result.get("summary", "")
        }
        
    except Exception as e:
        raise Exception(f"Error analyzing policy document: {str(e)}")

async def extract_policy_sections(analysis_result: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Extract structured policy sections from the AI analysis.
    
    Args:
        analysis_result: Result from analyze_policy_document
        
    Returns:
        List of policy sections
    """
    sections = []
    
    for category in analysis_result.get("categories", []):
        for rule in category.get("rules", []):
            section = {
                "title": f"{category['name']} - {rule['rule'][:50]}...",
                "content": rule["rule"],
                "category": category["name"].lower(),
                "severity": rule.get("severity", "medium"),
                "penalties": rule.get("penalties", [])
            }
            sections.append(section)
    
    return sections

async def generate_hoa_specific_prompt(hoa_id: int, policy_content: str) -> str:
    """
    Generate a HOA-specific prompt for violation analysis.
    
    Args:
        hoa_id: The HOA ID
        policy_content: The policy content to base the prompt on
        
    Returns:
        Customized prompt for this HOA
    """
    prompt = f"""
    You are an AI assistant for HOA {hoa_id} violation management.
    
    HOA POLICY CONTEXT:
    {policy_content[:2000]}
    
    When analyzing violations for this HOA, please:
    1. Reference the specific rules and regulations from their policy
    2. Use the violation types and categories defined in their policy
    3. Apply the severity levels and penalties as specified
    4. Maintain consistency with their enforcement procedures
    5. Use language and terminology that matches their policy
    
    Always prioritize the HOA's specific rules over general guidelines.
    """
    
    return prompt

async def generate_policy_aware_violation_analysis(
    violation_data: Dict[str, Any], 
    hoa_policies: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Generate violation analysis using HOA-specific policies.
    
    Args:
        violation_data: The violation information
        hoa_policies: List of HOA policy documents
        
    Returns:
        Policy-aware violation analysis
    """
    # Combine all policy content
    policy_content = "\n\n".join([p.get("content", "") for p in hoa_policies])
    
    prompt = f"""
    Analyze this violation using the HOA's specific policies:
    
    HOA POLICIES:
    {policy_content[:3000]}
    
    VIOLATION DETAILS:
    Description: {violation_data.get('description', '')}
    Address: {violation_data.get('address', '')}
    Severity: {violation_data.get('severity', 'medium')}
    
    Please provide:
    1. Policy violation assessment
    2. Applicable rules from their policy
    3. Recommended enforcement action
    4. Suggested letter content
    5. Appropriate tags and categories
    
    Format as JSON:
    {{
        "violation_assessment": "Assessment of the violation",
        "applicable_rules": ["List of applicable rules"],
        "enforcement_action": "Recommended action",
        "letter_content": "Draft letter content",
        "tags": ["relevant", "tags"],
        "category": "violation category"
    }}
    """
    
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are an expert HOA violation analyst."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3
    )
    
    return json.loads(response.choices[0].message.content)

async def train_ai_on_policy_corrections(
    hoa_id: int, 
    violation_id: int, 
    original_analysis: Dict[str, Any],
    user_corrections: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Train the AI system on user corrections for future improvements.
    
    Args:
        hoa_id: The HOA ID
        violation_id: The violation ID
        original_analysis: Original AI analysis
        user_corrections: User's corrections
        
    Returns:
        Training feedback for future improvements
    """
    # This would integrate with a vector database for storing corrections
    # For now, we'll return a simple feedback structure
    
    feedback = {
        "hoa_id": hoa_id,
        "violation_id": violation_id,
        "original_analysis": original_analysis,
        "user_corrections": user_corrections,
        "learning_points": [
            "Key learning points from the correction",
            "Patterns to apply in future analyses"
        ],
        "timestamp": "2024-01-01T00:00:00Z"
    }
    
    return feedback 