import os
import json
import re
from openai import OpenAI
from typing import Tuple, List
from core.config import get_settings
from utils.logger import get_logger
from sqlalchemy.orm import Session
from models import ContractRecord

# Get settings and logger
settings = get_settings()
logger = get_logger("summary_generator")

# 🔐 Load API client
client = OpenAI(api_key=settings.openai_api_key)

async def analyze_contract(contract: ContractRecord, db: Session) -> dict:
    """
    Analyze a contract using the comprehensive contract analyzer.
    Returns analysis results including summary, risks, and suggestions.
    """
    try:
        # Import the comprehensive analyzer
        from utils.contract_analyzer import analyze_contract_comprehensive
        
        # Use the comprehensive analysis
        return await analyze_contract_comprehensive(contract, db)
        
    except Exception as e:
        logger.error(f"Contract analysis failed: {e}")
        # Return fallback analysis
        return {
            "analysis_json": {},
            "summary": "Analysis failed. Please try again or contact support.",
            "risks": [],
            "suggestions": []
        }


