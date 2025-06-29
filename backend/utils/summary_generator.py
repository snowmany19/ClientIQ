import os
import json
import re
from openai import OpenAI

# 🔐 Load API client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 🌿 Allowed tags
FIXED_TAGS = [
    "Theft", "Verbal Threat", "Assault", "Trespassing", "Vandalism",
    "Weapon", "Suspicious Activity", "Employee Misconduct",
    "Customer Complaint", "Other", "Fraud"
]

def summarize_incident(description: str):
    prompt = f"""
You are a professional asset protection analyst responsible for documenting incidents at a national retail chain.

Your task is to:
1. Write a factual, concise summary suitable for an internal asset protection report
2. Include: what happened, when and where it occurred, involved individuals, and likely cause
3. Add a closing recommendation for store leadership
4. Use a formal, professional tone
5. Assign 1 to 5 tags from this fixed list:
{', '.join(FIXED_TAGS)}

Do not add tags not found in the list. Avoid sensationalism or vague language. Be direct and use proper terminology.

Respond strictly in this JSON format:
{{
  "summary": "<formal summary with recommendation>",
  "tags": ["Tag1", "Tag2", ...]
}}

Incident Description:
'{description}'
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )

        # 🧠 Extract content and clean JSON
        content = response.choices[0].message.content.strip()
        match = re.search(r"\{.*\}", content, re.DOTALL)
        if not match:
            raise ValueError("No JSON found in GPT response")

        json_text = match.group(0)
        result = json.loads(json_text)

        summary = result.get("summary", "").strip()
        tags = [tag for tag in result.get("tags", []) if tag in FIXED_TAGS]

        if not tags:
            tags = ["Other"]

        return summary, ", ".join(tags)

    except Exception as e:
        print(f"❌ GPT tag/summary generation failed: {e}")
        return f"GPT error: {e}", "Other"

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
        return int(response.choices[0].message.content.strip())
    except Exception as e:
        print(f"⚠️ Severity scoring failed: {e}")
        return 3  # Default fallback


