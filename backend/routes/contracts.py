# backend/routes/contracts.py
# ContractGuard.ai - Contract Management Routes

import os
import json
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from database import get_db
from models import ContractRecord, User, Workspace
from schemas import (
    ContractRecordCreate, ContractRecordUpdate, ContractRecordOut, 
    ContractRecordList, ContractAnalysisRequest, ContractAnalysisResponse
)
from utils.auth_utils import get_current_user
# from utils.plan_enforcement import check_contract_limit  # Temporarily commented out
from utils.summary_generator import analyze_contract
from utils.contract_analyzer import answer_contract_question
from utils.contract_pdf import generate_contract_analysis_pdf
from utils.logger import get_logger

logger = get_logger("contracts")

router = APIRouter(tags=["contracts"])

# ===========================
# 📄 Contract CRUD Operations
# ===========================

@router.post("/", response_model=ContractRecordOut)
async def create_contract(
    contract_data: ContractRecordCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new contract record."""
    try:
        # Debug logging
        logger.info(f"Received contract creation request from user {current_user.username}")
        logger.info(f"Contract data: {contract_data}")
        logger.info(f"Contract data type: {type(contract_data)}")
        logger.info(f"Contract data dict: {contract_data.dict()}")
        
        # Temporarily comment out plan enforcement to fix the issue
        # await check_contract_limit(current_user, db)
        
        # Create new contract record with proper defaults
        db_contract = ContractRecord(
            owner_user_id=current_user.id,
            title=contract_data.title,
            counterparty=contract_data.counterparty,
            category=contract_data.category,
            effective_date=contract_data.effective_date,
            term_end=contract_data.term_end,
            renewal_terms=getattr(contract_data, 'renewal_terms', None),
            governing_law=getattr(contract_data, 'governing_law', None),
            uploaded_files=getattr(contract_data, 'uploaded_files', []),
            status=getattr(contract_data, 'status', 'pending')
        )
        
        db.add(db_contract)
        db.commit()
        db.refresh(db_contract)
        
        # Add owner username for response
        contract_out = ContractRecordOut.from_orm(db_contract)
        contract_out.owner_username = current_user.username
        
        logger.info(f"Contract created: {db_contract.id} by user {current_user.username}")
        return contract_out
        
    except Exception as e:
        logger.error(f"Error creating contract: {str(e)}")
        logger.error(f"Contract data: {contract_data}")
        logger.error(f"User: {current_user.username} (ID: {current_user.id})")
        raise HTTPException(status_code=500, detail=f"Failed to create contract: {str(e)}")

@router.get("/list", response_model=ContractRecordList)
async def list_contracts(
    page: Optional[int] = Query(1, ge=1, description="Page number"),
    per_page: Optional[int] = Query(20, ge=1, le=100, description="Items per page"),
    category: Optional[str] = Query(None, description="Filter by category"),
    status: Optional[str] = Query(None, description="Filter by status"),
    search: Optional[str] = Query(None, description="Search in title or counterparty"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List contracts with pagination and filtering."""
    try:
        # Ensure we have valid defaults
        page = page or 1
        per_page = per_page or 20
        
        # Build query based on user role
        if current_user.role == "admin":
            query = db.query(ContractRecord)
        else:
            query = db.query(ContractRecord).filter(
                ContractRecord.owner_user_id == current_user.id
            )
        
        # Apply filters
        if category:
            query = query.filter(ContractRecord.category == category)
        if status:
            query = query.filter(ContractRecord.status == status)
        if search:
            search_filter = or_(
                ContractRecord.title.ilike(f"%{search}%"),
                ContractRecord.counterparty.ilike(f"%{search}%")
            )
            query = query.filter(search_filter)
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        contracts = query.offset((page - 1) * per_page).limit(per_page).all()
        
        # Convert to response format
        contract_list = []
        for contract in contracts:
            contract_out = ContractRecordOut.from_orm(contract)
            # Get owner username
            owner = db.query(User).filter(User.id == contract.owner_user_id).first()
            contract_out.owner_username = owner.username if owner else None
            contract_list.append(contract_out)
        
        result = ContractRecordList(
            contracts=contract_list,
            total=total,
            page=page,
            per_page=per_page
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error listing contracts: {e}")
        raise HTTPException(status_code=500, detail="Failed to list contracts")

# Move the specific contract route after the general list route
@router.get("/{contract_id}", response_model=ContractRecordOut)
async def get_contract(
    contract_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific contract by ID."""
    try:
        # Build query based on user role
        if current_user.role == "admin":
            contract = db.query(ContractRecord).filter(
                ContractRecord.id == contract_id
            ).first()
        else:
            contract = db.query(ContractRecord).filter(
                and_(
                    ContractRecord.id == contract_id,
                    ContractRecord.owner_user_id == current_user.id
                )
            ).first()
        
        if not contract:
            raise HTTPException(status_code=404, detail="Contract not found")
        
        # Convert to response format
        contract_out = ContractRecordOut.from_orm(contract)
        owner = db.query(User).filter(User.id == contract.owner_user_id).first()
        contract_out.owner_username = owner.username if owner else None
        
        return contract_out
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting contract {contract_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get contract")

@router.put("/{contract_id}", response_model=ContractRecordOut)
async def update_contract(
    contract_id: int,
    contract_data: ContractRecordUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a contract record."""
    try:
        # Get contract and check permissions
        if current_user.role == "admin":
            contract = db.query(ContractRecord).filter(
                ContractRecord.id == contract_id
            ).first()
        else:
            contract = db.query(ContractRecord).filter(
                and_(
                    ContractRecord.id == contract_id,
                    ContractRecord.owner_user_id == current_user.id
                )
            ).first()
        
        if not contract:
            raise HTTPException(status_code=404, detail="Contract not found")
        
        # Update fields
        update_data = contract_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(contract, field, value)
        
        contract.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(contract)
        
        # Convert to response format
        contract_out = ContractRecordOut.from_orm(contract)
        owner = db.query(User).filter(User.id == contract.owner_user_id).first()
        contract_out.owner_username = owner.username if owner else None
        
        logger.info(f"Contract updated: {contract_id} by user {current_user.username}")
        return contract_out
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating contract {contract_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to update contract")

@router.delete("/{contract_id}")
async def delete_contract(
    contract_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a contract record."""
    try:
        # Get contract and check permissions
        if current_user.role == "admin":
            contract = db.query(ContractRecord).filter(
                ContractRecord.id == contract_id
            ).first()
        else:
            contract = db.query(ContractRecord).filter(
                and_(
                    ContractRecord.id == contract_id,
                    ContractRecord.owner_user_id == current_user.id
                )
            ).first()
        
        if not contract:
            raise HTTPException(status_code=404, detail="Contract not found")
        
        # Delete the contract
        db.delete(contract)
        db.commit()
        
        logger.info(f"Contract deleted: {contract_id} by user {current_user.username}")
        return {"message": "Contract deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting contract {contract_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete contract")

# ===========================
# 🤖 AI Analysis Operations
# ===========================

@router.post("/analyze/{contract_id}", response_model=ContractAnalysisResponse)
async def analyze_contract_ai(
    contract_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Analyze a contract using AI."""
    try:
        # Get contract and check permissions
        if current_user.role == "admin":
            contract = db.query(ContractRecord).filter(
                ContractRecord.id == contract_id
            ).first()
        else:
            contract = db.query(ContractRecord).filter(
                and_(
                    ContractRecord.id == contract_id,
                    ContractRecord.owner_user_id == current_user.id
                )
            ).first()
        
        if not contract:
            raise HTTPException(status_code=404, detail="Contract not found")
        
        # Refresh the contract to get the latest data including uploaded_files
        db.refresh(contract)
        
        # Debug logging
        logger.info(f"Contract {contract_id} uploaded_files: {contract.uploaded_files}")
        logger.info(f"Contract {contract_id} uploaded_files type: {type(contract.uploaded_files)}")
        logger.info(f"Contract {contract_id} uploaded_files length: {len(contract.uploaded_files) if contract.uploaded_files else 0}")
        
        if not contract.uploaded_files:
            raise HTTPException(status_code=400, detail="No files uploaded for analysis")
        
        # Perform AI analysis
        analysis_result = await analyze_contract(contract, db)
        
        # Update contract with analysis results
        contract.analysis_json = analysis_result.get("analysis_json")
        contract.summary_text = analysis_result.get("summary")
        contract.risk_items = analysis_result.get("risks", [])
        contract.rewrite_suggestions = analysis_result.get("suggestions", [])
        contract.status = "analyzed"
        contract.updated_at = datetime.utcnow()
        
        db.commit()
        
        logger.info(f"Contract analyzed: {contract_id} by user {current_user.username}")
        
        return ContractAnalysisResponse(
            contract_id=contract_id,
            summary=analysis_result.get("summary", ""),
            risks=analysis_result.get("risks", []),
            suggestions=analysis_result.get("suggestions", []),
            analysis_completed=True
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing contract {contract_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to analyze contract")

# ===========================
# 📁 File Upload Operations
# ===========================

@router.post("/upload/{contract_id}")
async def upload_contract_file(
    contract_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload a file for a contract."""
    try:
        # Get contract and check permissions
        if current_user.role == "admin":
            contract = db.query(ContractRecord).filter(
                ContractRecord.id == contract_id
            ).first()
        else:
            contract = db.query(ContractRecord).filter(
                and_(
                    ContractRecord.id == contract_id,
                    ContractRecord.owner_user_id == current_user.id
                )
            ).first()
        
        if not contract:
            raise HTTPException(status_code=404, detail="Contract not found")
        
        # Validate file type
        allowed_extensions = ['.pdf', '.docx', '.doc', '.txt']
        file_extension = os.path.splitext(file.filename)[1].lower()
        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=400, 
                detail=f"File type not allowed. Allowed types: {', '.join(allowed_extensions)}"
            )
        
        # Create upload directory
        upload_dir = "static/documents"
        os.makedirs(upload_dir, exist_ok=True)
        
        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"contract_{contract_id}_{timestamp}_{file.filename}"
        file_path = os.path.join(upload_dir, filename)
        
        # Save file
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Update contract with new file
        if contract.uploaded_files is None:
            contract.uploaded_files = []
        
        # Create a new list with the file path instead of using append()
        current_files = list(contract.uploaded_files) if contract.uploaded_files else []
        current_files.append(file_path)
        contract.uploaded_files = current_files
        
        contract.updated_at = datetime.utcnow()
        
        # Debug logging
        logger.info(f"Before commit - Contract {contract_id} uploaded_files: {contract.uploaded_files}")
        logger.info(f"Before commit - Contract {contract_id} uploaded_files type: {type(contract.uploaded_files)}")
        
        db.commit()
        
        # Debug logging after commit
        logger.info(f"After commit - Contract {contract_id} uploaded_files: {contract.uploaded_files}")
        
        logger.info(f"File uploaded for contract {contract_id}: {filename}")
        return {"message": "File uploaded successfully", "filename": filename}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading file for contract {contract_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to upload file")

@router.get("/files/{contract_id}/{filename}")
async def get_contract_file(
    contract_id: int,
    filename: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a contract file by ID and filename."""
    try:
        # Verify user has access to this contract
        if current_user.role != "admin":
            contract = db.query(ContractRecord).filter(
                and_(
                    ContractRecord.id == contract_id,
                    ContractRecord.owner_user_id == current_user.id
                )
            ).first()
            if not contract:
                raise HTTPException(status_code=404, detail="Contract not found")
        
        # Get file path
        file_path = f"static/documents/contract_{contract_id}_{filename}"
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found")
        
        return FileResponse(file_path)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting contract file {contract_id}/{filename}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get contract file")

# ===========================
# 📊 Analytics Operations
# ===========================

@router.get("/analytics/summary")
async def get_contract_analytics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get contract analytics summary."""
    try:
        # Build query based on user role
        if current_user.role == "admin":
            query = db.query(ContractRecord)
        else:
            query = db.query(ContractRecord).filter(
                ContractRecord.owner_user_id == current_user.id
            )
        
        # Get counts by category
        categories = db.query(ContractRecord.category).distinct().all()
        category_counts = {}
        for category in categories:
            count = query.filter(ContractRecord.category == category[0]).count()
            category_counts[category[0]] = count
        
        # Get counts by status
        statuses = db.query(ContractRecord.status).distinct().all()
        status_counts = {}
        for status in statuses:
            count = query.filter(ContractRecord.status == status[0]).count()
            status_counts[status[0]] = count
        
        # Get total contracts
        total_contracts = query.count()
        
        # Get contracts analyzed this month
        from datetime import datetime, timedelta
        start_of_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        analyzed_this_month = query.filter(
            and_(
                ContractRecord.status == "analyzed",
                ContractRecord.updated_at >= start_of_month
            )
        ).count()
        
        return {
            "total_contracts": total_contracts,
            "analyzed_this_month": analyzed_this_month,
            "by_category": category_counts,
            "by_status": status_counts
        }
        
    except Exception as e:
        logger.error(f"Error getting contract analytics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get analytics")

# ===========================
# 🤖 Contract Q&A Operations
# ===========================

@router.post("/ask/{contract_id}")
async def ask_contract_question(
    contract_id: int,
    question: str = Form(..., description="Question about the contract"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Ask a specific question about a contract using AI."""
    try:
        # Get contract and check permissions
        if current_user.role == "admin":
            contract = db.query(ContractRecord).filter(
                ContractRecord.id == contract_id
            ).first()
        else:
            contract = db.query(ContractRecord).filter(
                and_(
                    ContractRecord.id == contract_id,
                    ContractRecord.owner_user_id == current_user.id
                )
            ).first()
        
        if not contract:
            raise HTTPException(status_code=404, detail="Contract not found")
        
        if not contract.uploaded_files:
            raise HTTPException(status_code=400, detail="No files uploaded for analysis")
        
        # Get AI answer
        answer = await answer_contract_question(contract, question, db)
        
        logger.info(f"Contract Q&A: {contract_id} by user {current_user.username}")
        
        return {
            "contract_id": contract_id,
            "question": question,
            "answer": answer
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error answering question for contract {contract_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to answer question")

# ===========================
# 📄 PDF Report Generation
# ===========================

@router.get("/report/{contract_id}")
async def generate_contract_report(
    contract_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate and download a contract analysis report."""
    try:
        # Verify user has access to this contract
        if current_user.role != "admin":
            contract = db.query(ContractRecord).filter(
                and_(
                    ContractRecord.id == contract_id,
                    ContractRecord.owner_user_id == current_user.id
                )
            ).first()
            if not contract:
                raise HTTPException(status_code=404, detail="Contract not found")
        
        # Generate report
        report_path = await generate_contract_analysis_pdf(contract_id, db)
        
        if not report_path or not os.path.exists(report_path):
            raise HTTPException(status_code=500, detail="Failed to generate report")
        
        return FileResponse(
            report_path,
            filename=f"contract_analysis_{contract_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating report for contract {contract_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate report")
