import os
import json
import re
from openai import OpenAI
from typing import Tuple, List
from core.config import get_settings
from utils.logger import get_logger

# Get settings and logger
settings = get_settings()
logger = get_logger("summary_generator")

# 🔐 Load API client
client = OpenAI(api_key=settings.openai_api_key)

# 🌿 Allowed tags
FIXED_TAGS = [
    "Theft", "Verbal Threat", "Assault", "Trespassing", "Vandalism",
    "Weapon", "Suspicious Activity", "Employee Misconduct",
    "Customer Complaint", "Other", "Fraud"
]

def summarize_incident(description: str, location: str, timestamp: str) -> Tuple[str, List[str]]:
    """
    Generate a summary and tags for an incident using OpenAI GPT-4.
    Returns (summary, tags_list)
    """
    prompt = f"""
You are an incident management AI assistant. Analyze the following security incident and provide:
1. A concise summary (2-3 sentences)
2. Relevant tags (choose ONLY from the allowed tags list)

Incident Details:
- Description: {description}
- Location: {location}
- Timestamp: {timestamp}

ALLOWED TAGS (choose only from these):
{', '.join(FIXED_TAGS)}

Rules:
- Choose 1-3 most relevant tags from the allowed list above
- Do NOT create new tags
- Do NOT use tags not in the allowed list
- Separate multiple tags with commas

Respond in this exact format:
SUMMARY: [your summary here]
TAGS: [tag1, tag2, tag3]
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=200
        )
        
        content = response.choices[0].message.content
        if content is None:
            logger.error("Empty response from GPT")
            return f"Incident reported at {location} on {timestamp}. {description[:100]}...", ["Other"]
        
        content = content.strip()
        
        # Parse response
        lines = content.split('\n')
        summary = ""
        tags = []
        
        for line in lines:
            if line.startswith('SUMMARY:'):
                summary = line.replace('SUMMARY:', '').strip()
            elif line.startswith('TAGS:'):
                tags_str = line.replace('TAGS:', '').strip()
                raw_tags = [tag.strip() for tag in tags_str.split(',') if tag.strip()]
                # Filter to only allow tags from FIXED_TAGS
                tags = [tag for tag in raw_tags if tag in FIXED_TAGS]
                # If no valid tags found, use "Other"
                if not tags:
                    tags = ["Other"]
        
        return summary, tags
        
    except Exception as e:
        logger.error(f"GPT tag/summary generation failed: {e}")
        # Fallback response
        return f"Incident reported at {location} on {timestamp}. {description[:100]}...", ["Other"]

def classify_severity(summary: str) -> int:
    prompt = f"""
You are a risk assessment model.
Rate the severity of the following security incident from 1 (Low) to 5 (Critical):

Severity Criteria:
1 = Minor nuisance or false report
2 = Mild disruption, low threat (e.g. verbal complaint)
3 = Moderate disruption or verbal threat
4 = Physical altercation, theft, or confirmed policy violation
5 = Weapon involved, law enforcement required, or major security breach

Incident Summary:
'{summary}'

Respond ONLY with a single integer from 1 to 5.
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        content = response.choices[0].message.content
        if content is None:
            logger.error("Empty response from GPT for severity classification")
            return 3  # Default fallback
        return int(content.strip())
    except Exception as e:
        logger.warning(f"Severity scoring failed: {e}")
        return 3  # Default fallback


