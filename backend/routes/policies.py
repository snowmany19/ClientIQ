# backend/routes/policies.py

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session
from typing import List, Optional
import json

from database import get_db
from models import User, PolicyDocument, PolicySection
from utils.auth_utils import get_current_user
from utils.plan_enforcement import require_active_subscription, require_plan_feature
from utils.ai_policy_analyzer import (
    analyze_policy_document, 
    extract_policy_sections,
    generate_hoa_specific_prompt,
    generate_policy_aware_violation_analysis
)

router = APIRouter()

@router.post("/upload")
async def upload_policy_document(
    file: UploadFile = File(...),
    name: str = Form(...),
    current_user: User = Depends(require_active_subscription),
    db: Session = Depends(get_db)
):
    """
    Upload and analyze a policy document for Business-tier and higher.
    """
    # Check if user has access to policy features
    if current_user.role not in ["admin", "hoa_board"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins and HOA board members can upload policies"
        )
    
    # Validate file type
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are supported"
        )
    
    try:
        # Read file content
        content = await file.read()
        
        # Analyze the policy document using AI
        analysis_result = await analyze_policy_document(content)
        
        # Create policy document record
        policy_doc = PolicyDocument(
            hoa_id=current_user.hoa_id,
            name=name,
            content=analysis_result["full_text"],
            uploaded_by=current_user.id,
            status="draft"
        )
        
        db.add(policy_doc)
        db.commit()
        db.refresh(policy_doc)
        
        # Extract and create policy sections
        sections = await extract_policy_sections(analysis_result["ai_analysis"])
        
        for section_data in sections:
            section = PolicySection(
                policy_id=policy_doc.id,
                title=section_data["title"],
                content=section_data["content"],
                category=section_data["category"],
                severity=section_data["severity"],
                penalties=section_data["penalties"]
            )
            db.add(section)
        
        db.commit()
        
        return {
            "message": "Policy document uploaded and analyzed successfully",
            "policy_id": policy_doc.id,
            "analysis": {
                "violation_types": analysis_result["violation_types"],
                "tags": analysis_result["tags"],
                "summary": analysis_result["summary"],
                "sections_count": len(sections)
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing policy document: {str(e)}"
        )

@router.get("/")
async def get_policy_documents(
    current_user: User = Depends(require_active_subscription),
    db: Session = Depends(get_db)
):
    """
    Get all policy documents for the user's HOA.
    """
    policies = db.query(PolicyDocument).filter(
        PolicyDocument.hoa_id == current_user.hoa_id
    ).all()
    
    return [
        {
            "id": policy.id,
            "name": policy.name,
            "version": policy.version,
            "status": policy.status,
            "effective_date": policy.effective_date,
            "created_at": policy.created_at,
            "sections_count": len(policy.sections)
        }
        for policy in policies
    ]

@router.get("/{policy_id}")
async def get_policy_details(
    policy_id: int,
    current_user: User = Depends(require_active_subscription),
    db: Session = Depends(get_db)
):
    """
    Get detailed information about a specific policy document.
    """
    policy = db.query(PolicyDocument).filter(
        PolicyDocument.id == policy_id,
        PolicyDocument.hoa_id == current_user.hoa_id
    ).first()
    
    if not policy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Policy document not found"
        )
    
    return {
        "id": policy.id,
        "name": policy.name,
        "content": policy.content,
        "version": policy.version,
        "status": policy.status,
        "effective_date": policy.effective_date,
        "created_at": policy.created_at,
        "sections": [
            {
                "id": section.id,
                "title": section.title,
                "content": section.content,
                "category": section.category,
                "severity": section.severity,
                "penalties": section.penalties
            }
            for section in policy.sections
        ]
    }

@router.put("/{policy_id}/activate")
async def activate_policy_document(
    policy_id: int,
    current_user: User = Depends(require_active_subscription),
    db: Session = Depends(get_db)
):
    """
    Activate a policy document and deactivate others.
    """
    if current_user.role not in ["admin", "hoa_board"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins and HOA board members can activate policies"
        )
    
    # Deactivate all other policies for this HOA
    db.query(PolicyDocument).filter(
        PolicyDocument.hoa_id == current_user.hoa_id,
        PolicyDocument.status == "active"
    ).update({"status": "archived"})
    
    # Activate the specified policy
    policy = db.query(PolicyDocument).filter(
        PolicyDocument.id == policy_id,
        PolicyDocument.hoa_id == current_user.hoa_id
    ).first()
    
    if not policy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Policy document not found"
        )
    
    policy.status = "active"
    db.commit()
    
    return {"message": "Policy document activated successfully"}

@router.delete("/{policy_id}")
async def delete_policy_document(
    policy_id: int,
    current_user: User = Depends(require_active_subscription),
    db: Session = Depends(get_db)
):
    """
    Delete a policy document.
    """
    if current_user.role not in ["admin", "hoa_board"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins and HOA board members can delete policies"
        )
    
    policy = db.query(PolicyDocument).filter(
        PolicyDocument.id == policy_id,
        PolicyDocument.hoa_id == current_user.hoa_id
    ).first()
    
    if not policy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Policy document not found"
        )
    
    db.delete(policy)
    db.commit()
    
    return {"message": "Policy document deleted successfully"}

@router.post("/{policy_id}/sections")
async def add_policy_section(
    policy_id: int,
    title: str = Form(...),
    content: str = Form(...),
    category: str = Form(...),
    severity: str = Form(default="medium"),
    penalties: str = Form(default="[]"),
    current_user: User = Depends(require_active_subscription),
    db: Session = Depends(get_db)
):
    """
    Add a new section to a policy document.
    """
    if current_user.role not in ["admin", "hoa_board"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins and HOA board members can add policy sections"
        )
    
    policy = db.query(PolicyDocument).filter(
        PolicyDocument.id == policy_id,
        PolicyDocument.hoa_id == current_user.hoa_id
    ).first()
    
    if not policy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Policy document not found"
        )
    
    try:
        penalties_list = json.loads(penalties)
    except json.JSONDecodeError:
        penalties_list = []
    
    section = PolicySection(
        policy_id=policy_id,
        title=title,
        content=content,
        category=category,
        severity=severity,
        penalties=penalties_list
    )
    
    db.add(section)
    db.commit()
    db.refresh(section)
    
    return {
        "message": "Policy section added successfully",
        "section_id": section.id
    }

@router.get("/ai/status")
async def get_ai_training_status(
    current_user: User = Depends(require_active_subscription),
    db: Session = Depends(get_db)
):
    """
    Get AI training status for Pro and Enterprise tiers.
    """
    # Check if user has Pro or Enterprise tier (this would be implemented in plan enforcement)
    # For now, we'll return a basic status
    
    active_policies = db.query(PolicyDocument).filter(
        PolicyDocument.hoa_id == current_user.hoa_id,
        PolicyDocument.status == "active"
    ).count()
    
    return {
        "ai_enabled": True,  # This would be based on subscription tier
        "active_policies": active_policies,
        "training_data_points": 0,  # This would track actual training data
        "last_training": None,
        "model_accuracy": "N/A"
    } 