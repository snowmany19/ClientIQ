import os
import json
import re
from openai import OpenAI
from typing import Tuple, List
from core.config import get_settings
from utils.logger import get_logger
from sqlalchemy.orm import Session
from models import Violation

# Get settings and logger
settings = get_settings()
logger = get_logger("summary_generator")

# 🔐 Load API client
client = OpenAI(api_key=settings.openai_api_key)

# 🌿 Allowed tags for HOA violations
FIXED_TAGS = [
    "Landscaping", "Trash", "Parking", "Exterior Maintenance", "Noise",
    "Pet Violation", "Architectural", "Pool/Spa", "Vehicle Storage",
    "Holiday Decorations", "Other", "Safety Hazard"
]

def summarize_violation(description: str, location: str, timestamp: str) -> Tuple[str, List[str]]:
    """
    Generate a summary and tags for a violation using OpenAI GPT-4.
    Returns (summary, tags_list) - tags are selected from predefined list only
    """
    prompt = f"""
You are an HOA violation analysis expert. Analyze this violation and provide:
1. A concise summary (2-3 sentences)
2. Select relevant tags from this EXACT list only: {', '.join(FIXED_TAGS)}

Violation Description: {description}
Location: {location}
Timestamp: {timestamp}

IMPORTANT: For tags, you MUST ONLY choose from this exact list: {', '.join(FIXED_TAGS)}
Do not create new tags. If none fit perfectly, choose the closest one or "Other".

Respond in this exact format:
SUMMARY: [your summary here]
TAGS: [tag1, tag2, tag3] (only from the allowed list)
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        content = response.choices[0].message.content
        if content is None:
            logger.error("Empty response from GPT for violation summary")
            return "Violation reported and documented.", ["Other"]
        
        # Parse response
        lines = content.split('\n')
        summary = "Violation reported and documented."
        tags = ["Other"]
        
        for line in lines:
            if line.startswith("SUMMARY:"):
                summary = line.replace("SUMMARY:", "").strip()
            elif line.startswith("TAGS:"):
                tags_str = line.replace("TAGS:", "").strip()
                # Clean up the tags string and extract individual tags
                tags_str = tags_str.replace('[', '').replace(']', '')
                raw_tags = [tag.strip() for tag in tags_str.split(',') if tag.strip()]
                
                # Filter tags to only include those from FIXED_TAGS
                valid_tags = []
                for tag in raw_tags:
                    # Find the closest match from FIXED_TAGS
                    for fixed_tag in FIXED_TAGS:
                        if tag.lower() == fixed_tag.lower():
                            valid_tags.append(fixed_tag)
                            break
                    else:
                        # If no exact match, try partial matching
                        for fixed_tag in FIXED_TAGS:
                            if tag.lower() in fixed_tag.lower() or fixed_tag.lower() in tag.lower():
                                valid_tags.append(fixed_tag)
                                break
                
                # If no valid tags found, use "Other"
                if valid_tags:
                    tags = valid_tags
                else:
                    tags = ["Other"]
        
        return summary, tags
        
    except Exception as e:
        logger.error(f"GPT tag/summary generation failed: {e}")
        return "Violation reported and documented.", ["Other"]

def calculate_repeat_offender_score(address: str, offender: str, db: Session) -> int:
    """Calculate repeat offender score based on existing violations in database."""
    try:
        # Count existing violations for this address or offender
        existing_violations = db.query(Violation).filter(
            (Violation.address.ilike(f"%{address}%")) |
            (Violation.offender.ilike(f"%{offender}%"))
        ).count()
        
        # Calculate score based on violation count
        if existing_violations == 0:
            return 1  # First-time violation
        elif existing_violations == 1:
            return 2  # Second violation
        elif existing_violations == 2:
            return 3  # Third violation - pattern developing
        elif existing_violations == 3:
            return 4  # Fourth violation - established pattern
        else:
            return 5  # Fifth+ violation - chronic offender
            
    except Exception as e:
        logger.warning(f"Failed to calculate repeat offender score: {e}")
        return 1  # Default fallback

def classify_repeat_offender_score(summary: str) -> int:
    prompt = f"""
You are a repeat offender assessment model for HOA violations.
Rate the likelihood of this being a repeat offender from 1 (First-time) to 5 (Chronic violator):

Repeat Offender Criteria:
1 = First-time violation, minor issue
2 = Second violation, moderate issue
3 = Third violation, consistent pattern developing
4 = Fourth violation, established pattern of non-compliance
5 = Fifth+ violation, chronic violator requiring escalated action

Violation Summary:
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
            logger.error("Empty response from GPT for repeat offender classification")
            return 1  # Default fallback
        return int(content.strip())
    except Exception as e:
        logger.warning(f"Repeat offender scoring failed: {e}")
        return 1  # Default fallback


