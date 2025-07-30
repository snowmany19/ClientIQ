# Violation routes
# routes/violations.py

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Query
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from typing import List, Optional
from database import get_db
from models import Violation, User, HOA, Resident
from schemas import ViolationCreate, ViolationOut
from utils.auth_utils import get_current_user, require_role, decode_token, require_active_subscription
from utils.plan_enforcement import check_violation_limit, require_plan_feature
from utils.image_uploader import save_image, extract_gps_from_image
from utils.pdf import generate_pdf
from utils.summary_generator import summarize_violation, classify_repeat_offender_score, calculate_repeat_offender_score
from utils.email_alerts import send_violation_notification_email
from utils.logger import get_logger
from utils.validation import InputValidator, ValidationException
from utils.workflow import trigger_violation_workflow
from utils.celery_tasks import generate_violation_pdf_async, send_email_notification_async, process_image_upload_async
from utils.cache import invalidate_user_cache, invalidate_hoa_cache
import tzlocal
import os
from fastapi.responses import FileResponse, StreamingResponse
import shutil
import csv
import io
import openai
from pydantic import BaseModel

router = APIRouter(prefix="/violations", tags=["Violations"])
REPORTS_DIR = "static/reports"

# Initialize logger
logger = get_logger("violations")

# 🔐 RBAC: Check if user can access HOA data
def can_access_hoa(user: User, hoa_name: str, db: Session) -> bool:
    if user.role == "admin":
        return True  # Admins can access all HOAs
    
    if user.role in ["inspector", "hoa_board"]:
        # Check if user's HOA matches the violation HOA
        if user.hoa_id is not None:
            user_hoa = db.query(HOA).filter(HOA.id == user.hoa_id).first()
            if user_hoa is not None:
                # Compare HOA numbers (e.g., "066" vs "066")
                user_hoa_number = f"HOA #{user_hoa.id:03d}"
                if user_hoa_number == hoa_name:
                    return True
        # Fallback: check if hoa_name matches user's assigned HOA
        return getattr(user, 'hoa_name', None) == hoa_name
    
    return False

@router.post("/", response_model=ViolationOut)
def create_violation(
    description: str = Form(...),
    hoa: str = Form(...),
    address: str = Form(...),
    location: str = Form(...),
    offender: str = Form(...),
    gps_coordinates: Optional[str] = Form(None),
    violation_type: Optional[str] = Form(None),
    file: UploadFile = File(None),
    mobile_capture: Optional[bool] = Form(False),  # New: indicates mobile capture
    auto_gps: Optional[bool] = Form(False),  # New: auto-detect GPS from image
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_active_subscription),
    __: bool = Depends(check_violation_limit),
):
    # 🔍 Input Validation (centralized)
    try:
        validated_description = InputValidator.validate_violation_description(description)
        validated_hoa = InputValidator.validate_hoa_name(hoa)
        validated_address = InputValidator.validate_address(address)
        validated_location = InputValidator.validate_location(location)
        validated_offender = InputValidator.validate_offender(offender)
        InputValidator.validate_file_upload(file)
    except ValidationException as ve:
        raise HTTPException(status_code=400, detail=str(ve))

    # 🔐 RBAC: Check if user can submit violations for this HOA
    if not can_access_hoa(current_user, validated_hoa, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied. You can only submit violations for your assigned HOA."
        )
    
    # 📱 Mobile-specific enhancements
    final_gps_coordinates = gps_coordinates
    
    # Auto-extract GPS from image if requested and no GPS provided
    if auto_gps and not gps_coordinates and file:
        try:
            extracted_gps = extract_gps_from_image(file)
            if extracted_gps:
                final_gps_coordinates = extracted_gps
                logger.info(f"Auto-extracted GPS coordinates: {extracted_gps}")
        except Exception as e:
            logger.warning(f"Failed to extract GPS from image: {e}")

    # 🏠 Find or create HOA
    hoa_obj = db.query(HOA).filter(HOA.name == validated_hoa).first()
    if not hoa_obj:
        hoa_obj = HOA(name=validated_hoa, location="Unknown")
        db.add(hoa_obj)
        db.flush()  # Get the ID

    # 🏠 Find or create resident
    resident = db.query(Resident).filter(
        Resident.address == validated_address,
        Resident.hoa_id == hoa_obj.id
    ).first()
    
    if not resident:
        resident = Resident(
            name=validated_offender,
            address=validated_address,
            hoa_id=hoa_obj.id
        )
        db.add(resident)
        db.flush()

    # 📸 Handle image upload
    image_url = None
    if file:
        try:
            image_url = save_image(file)
            logger.info(f"Image saved: {image_url}")
        except Exception as e:
            logger.error(f"Failed to save image: {e}")
            raise HTTPException(status_code=500, detail="Failed to save image")

    # 🤖 AI Processing (async)
    try:
        # Generate summary using OpenAI
        summary = summarize_violation(validated_description)
        
        # Classify repeat offender score
        repeat_offender_score = classify_repeat_offender_score(validated_description, validated_offender)
        
        # Calculate final repeat offender score
        final_repeat_score = calculate_repeat_offender_score(
            validated_offender, 
            validated_address, 
            repeat_offender_score,
            db
        )
        
        logger.info(f"AI processing completed - Summary: {len(summary)} chars, Score: {final_repeat_score}")
        
    except Exception as e:
        logger.error(f"AI processing failed: {e}")
        # Fallback values
        summary = f"Violation report: {validated_description[:200]}..."
        final_repeat_score = 1

    # 📝 Create violation record
    violation = Violation(
        description=validated_description,
        summary=summary,
        hoa_name=validated_hoa,
        address=validated_address,
        location=validated_location,
        offender=validated_offender,
        gps_coordinates=final_gps_coordinates,
        repeat_offender_score=final_repeat_score,
        image_url=image_url,
        user_id=current_user.id,
        hoa_id=hoa_obj.id
    )
    
    db.add(violation)
    db.commit()
    db.refresh(violation)
    
    # 🔄 Trigger background tasks
    try:
        # Generate PDF asynchronously
        generate_violation_pdf_async.delay(violation.id)
        
        # Send email notification asynchronously
        send_email_notification_async.delay(current_user.id, violation.id)
        
        # Process image asynchronously if uploaded
        if image_url:
            process_image_upload_async.delay(image_url, violation.id)
        
        logger.info(f"Background tasks triggered for violation {violation.id}")
    except Exception as e:
        logger.error(f"Failed to trigger background tasks: {e}")
        # Don't fail the request if background tasks fail
    
    # 🧹 Invalidate related caches
    try:
        invalidate_user_cache(current_user.id)
        invalidate_hoa_cache(hoa_obj.id)
    except Exception as e:
        logger.warning(f"Cache invalidation failed: {e}")
    
    # 🔄 Trigger workflow
    try:
        trigger_violation_workflow(violation, current_user, db)
    except Exception as e:
        logger.error(f"Workflow trigger failed: {e}")

    # 📊 Update resident violation count
    resident.violation_count += 1
    db.commit()

    logger.info(f"Violation created successfully: {violation.id}")
    
    return violation

@router.get("/")
def get_all_violations(
    skip: int = 0,
    limit: int = 50,
    hoa_id: Optional[int] = None,
    tag: Optional[str] = None,
    resident_id: Optional[int] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_active_subscription),
):
    from sqlalchemy import text
    
    # 🔍 Input validation for pagination
    if skip < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Skip must be 0 or greater."
        )
    
    if limit < 1 or limit > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Limit must be between 1 and 100."
        )
    
    # 🔐 RBAC: Filter violations based on user role using SQLAlchemy ORM
    query = db.query(Violation)
    
    if current_user.role == "admin":
        # Admins can see all violations
        pass
    elif current_user.role in ["inspector", "hoa_board"]:
        # Inspectors and HOA board can only see violations from their HOA
        if current_user.hoa_id is not None:
            user_hoa = db.query(HOA).filter(HOA.id == current_user.hoa_id).first()
            if user_hoa is not None:
                # Filter by HOA number (e.g., "HOA #066") instead of HOA name
                user_hoa_number = f"HOA #{user_hoa.id:03d}"
                query = query.filter(Violation.hoa_name == user_hoa_number)
            else:
                # Fallback: no HOA assigned, return empty
                return {"data": [], "pagination": {"total": 0, "pages": 0, "current_page": 1, "items_per_page": limit}}
        else:
            # No HOA assigned, return empty
            return {"data": [], "pagination": {"total": 0, "pages": 0, "current_page": 1, "items_per_page": limit}}
    else:
        # Unknown role, return empty
        return {"data": [], "pagination": {"total": 0, "pages": 0, "current_page": 1, "items_per_page": limit}}
    
    # Apply additional filters
    if hoa_id is not None:
        query = query.filter(Violation.hoa_id == hoa_id)
    
    if tag is not None:
        query = query.filter(Violation.tags.contains(tag))
    
    if resident_id is not None:
        query = query.filter(Violation.resident_id == resident_id)
    
    if status is not None:
        query = query.filter(Violation.status == status)
    
    # Get total count for pagination
    total = query.count()
    
    # Apply ordering and pagination
    query = query.order_by(Violation.timestamp.desc()).offset(skip).limit(limit)
    
    # Execute query
    try:
        violations = query.all()
    except Exception as e:
        logger.error(f"Error getting violations: {e}")
        violations = []
    
    items_per_page = limit
    pages = (total + items_per_page - 1) // items_per_page
    current_page = (skip // items_per_page) + 1
    
    # Convert to response format
    violations_data = []
    for violation in violations:
        violations_data.append({
            "id": violation.id,
            "violation_number": violation.violation_number,
            "timestamp": violation.timestamp,
            "description": violation.description,
            "summary": violation.summary,
            "tags": violation.tags,
            "repeat_offender_score": violation.repeat_offender_score,
            "hoa_name": violation.hoa_name,
            "address": violation.address,
            "location": violation.location,
            "offender": violation.offender,
            "gps_coordinates": violation.gps_coordinates,
            "status": violation.status,
            "pdf_path": violation.pdf_path,
            "image_url": violation.image_url,
            "user_id": violation.user_id,
            "inspected_by": violation.user.username if violation.user else None,
        })
    
    return {
        "data": violations_data,
        "pagination": {
            "total": total,
            "pages": pages,
            "current_page": current_page,
            "items_per_page": items_per_page
        }
    }

@router.get("/hoas/accessible")
def get_accessible_hoas(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get HOAs accessible to the current user."""
    if current_user.role == "admin":
        # Admins can access all HOAs
        hoas = db.query(HOA).all()
    elif current_user.role in ["inspector", "hoa_board"]:
        # Users can only access their assigned HOA
        if current_user.hoa_id is not None:
            hoas = db.query(HOA).filter(HOA.id == current_user.hoa_id).all()
        else:
            hoas = []
    else:
        hoas = []
    
    return [
        {
            "id": hoa.id,
            "hoa_number": f"HOA #{hoa.id:03d}",
            "name": hoa.name,
            "location": hoa.location
        }
        for hoa in hoas
    ]



@router.get("/pagination-info")
def get_pagination_info(
    hoa_id: Optional[int] = None,
    tag: Optional[str] = None,
    resident_id: Optional[int] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from sqlalchemy import text
    
    # 🔐 RBAC: Filter violations based on user role (same logic as get_all_violations)
    if current_user.role == "admin":
        count_query = "SELECT COUNT(*) FROM violations"
        where_conditions = []
    elif current_user.role in ["inspector", "hoa_board"]:
        if current_user.hoa_id is not None:
            user_hoa = db.query(HOA).filter(HOA.id == current_user.hoa_id).first()
            if user_hoa is not None:
                user_hoa_number = f"HOA #{user_hoa.id:03d}"
                count_query = "SELECT COUNT(*) FROM violations WHERE hoa_name = :hoa_name"
                where_conditions = [{"hoa_name": user_hoa_number}]
            else:
                return {"total": 0, "pages": 0, "current_page": 1, "items_per_page": 50}
        else:
            return {"total": 0, "pages": 0, "current_page": 1, "items_per_page": 50}
    else:
        return {"total": 0, "pages": 0, "current_page": 1, "items_per_page": 50}
    
    # Apply filters
    if hoa_id is not None:
        count_query += " WHERE hoa_id = :hoa_id" if "WHERE" not in count_query else " AND hoa_id = :hoa_id"
        where_conditions.append({"hoa_id": hoa_id})
    if tag is not None:
        count_query += " WHERE tags LIKE :tag" if "WHERE" not in count_query else " AND tags LIKE :tag"
        where_conditions.append({"tag": f"%{tag}%"})
    if resident_id is not None:
        count_query += " WHERE resident_id = :resident_id" if "WHERE" not in count_query else " AND resident_id = :resident_id"
        where_conditions.append({"resident_id": resident_id})
    if status is not None:
        count_query += " WHERE status = :status" if "WHERE" not in count_query else " AND status = :status"
        where_conditions.append({"status": status})
    
    # Get total count using raw SQL
    try:
        # Merge all where conditions
        params = {}
        for condition in where_conditions:
            params.update(condition)
        
        total_result = db.execute(text(count_query), params)
        total = total_result.scalar()
    except Exception as e:
        logger.error(f"Error getting violation count: {e}")
        total = 0
    
    items_per_page = 50
    pages = (total + items_per_page - 1) // items_per_page
    
    return {
        "total": total,
        "pages": pages,
        "current_page": 1,
        "items_per_page": items_per_page
    }

@router.get("/dashboard-data")
def get_dashboard_data(
    skip: int = 0,
    limit: int = 50,
    hoa_id: Optional[int] = None,
    tag: Optional[str] = None,
    resident_id: Optional[int] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_active_subscription),
):
    """Get all dashboard data in a single optimized call."""
    
    # 🔐 RBAC: Filter violations based on user role using SQLAlchemy ORM
    query = db.query(Violation)
    
    if current_user.role == "admin":
        # Admins can see all violations
        pass
    elif current_user.role in ["inspector", "hoa_board"]:
        if current_user.hoa_id is not None:
            user_hoa = db.query(HOA).filter(HOA.id == current_user.hoa_id).first()
            if user_hoa is not None:
                user_hoa_number = f"HOA #{user_hoa.id:03d}"
                query = query.filter(Violation.hoa_name == user_hoa_number)
            else:
                return {
                    "violations": [],
                    "pagination": {"total": 0, "pages": 0, "current_page": 1, "items_per_page": 50},
                    "accessible_hoas": []
                }
        else:
            return {
                "violations": [],
                "pagination": {"total": 0, "pages": 0, "current_page": 1, "items_per_page": 50},
                "accessible_hoas": []
            }
    else:
        return {
            "violations": [],
            "pagination": {"total": 0, "pages": 0, "current_page": 1, "items_per_page": 50},
            "accessible_hoas": []
        }
    
    # Apply filters
    if hoa_id is not None:
        query = query.filter(Violation.hoa_id == hoa_id)
    
    if tag is not None:
        query = query.filter(Violation.tags.contains(tag))
    
    if resident_id is not None:
        query = query.filter(Violation.resident_id == resident_id)
    
    if status is not None:
        query = query.filter(Violation.status == status)
    
    # Get total count for pagination
    total = query.count()
    
    items_per_page = 50
    pages = (total + items_per_page - 1) // items_per_page
    
    # Apply ordering and pagination
    query = query.order_by(Violation.timestamp.desc()).offset(skip).limit(limit)
    
    try:
        violations = query.all()
    except Exception as e:
        logger.error(f"Error getting violations: {e}")
        violations = []
    
    # Convert to response format
    violations_data = []
    for violation in violations:
        violations_data.append({
            "id": violation.id,
            "violation_number": violation.violation_number,
            "timestamp": violation.timestamp,
            "description": violation.description,
            "summary": violation.summary,
            "tags": violation.tags,
            "repeat_offender_score": violation.repeat_offender_score,
            "hoa_name": violation.hoa_name,
            "address": violation.address,
            "location": violation.location,
            "offender": violation.offender,
            "gps_coordinates": violation.gps_coordinates,
            "status": violation.status,
            "pdf_path": violation.pdf_path,
            "image_url": violation.image_url,
            "user_id": violation.user_id,
            "inspected_by": violation.user.username if violation.user else None,
        })
    
    # Get accessible HOAs
    accessible_hoas = get_accessible_hoas(db, current_user)
    
    return {
        "violations": violations_data,
        "pagination": {
            "total": total,
            "pages": pages,
            "current_page": (skip // items_per_page) + 1,
            "items_per_page": items_per_page
        },
        "accessible_hoas": accessible_hoas
    }

@router.get("/export-csv")
def export_violations_csv(
    skip: int = 0,
    limit: int = 1000,  # Allow larger export
    hoa_id: Optional[int] = None,
    tag: Optional[str] = None,
    resident_id: Optional[int] = None,
    status: Optional[str] = None,
    start_date: Optional[str] = None,  # ISO format
    end_date: Optional[str] = None,    # ISO format
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_active_subscription),
):
    """Export violations to CSV format."""
    from sqlalchemy import text
    
    # 🔐 RBAC: Filter violations based on user role (same logic as get_all_violations)
    if current_user.role == "admin":
        base_query = "SELECT * FROM violations"
        where_conditions = []
    elif current_user.role in ["inspector", "hoa_board"]:
        if current_user.hoa_id is not None:
            user_hoa = db.query(HOA).filter(HOA.id == current_user.hoa_id).first()
            if user_hoa is not None:
                user_hoa_number = f"HOA #{user_hoa.id:03d}"
                base_query = "SELECT * FROM violations WHERE hoa_name = :hoa_name"
                where_conditions = [{"hoa_name": user_hoa_number}]
            else:
                return StreamingResponse(
                    io.StringIO("No data available"),
                    media_type="text/csv",
                    headers={"Content-Disposition": "attachment; filename=violations.csv"}
                )
        else:
            return StreamingResponse(
                io.StringIO("No data available"),
                media_type="text/csv",
                headers={"Content-Disposition": "attachment; filename=violations.csv"}
            )
    else:
        return StreamingResponse(
            io.StringIO("No data available"),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=violations.csv"}
        )
    
    # Apply filters
    if hoa_id is not None:
        base_query += " WHERE hoa_id = :hoa_id" if "WHERE" not in base_query else " AND hoa_id = :hoa_id"
        where_conditions.append({"hoa_id": hoa_id})
    if tag is not None:
        base_query += " WHERE tags LIKE :tag" if "WHERE" not in base_query else " AND tags LIKE :tag"
        where_conditions.append({"tag": f"%{tag}%"})
    if resident_id is not None:
        base_query += " WHERE resident_id = :resident_id" if "WHERE" not in base_query else " AND resident_id = :resident_id"
        where_conditions.append({"resident_id": resident_id})
    if status is not None:
        base_query += " WHERE status = :status" if "WHERE" not in base_query else " AND status = :status"
        where_conditions.append({"status": status})
    
    # Apply date filters if provided
    if start_date:
        try:
            start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            base_query += " WHERE timestamp >= :start_date" if "WHERE" not in base_query else " AND timestamp >= :start_date"
            where_conditions.append({"start_date": start_dt})
        except ValueError:
            pass
    
    if end_date:
        try:
            end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            base_query += " WHERE timestamp <= :end_date" if "WHERE" not in base_query else " AND timestamp <= :end_date"
            where_conditions.append({"end_date": end_dt})
        except ValueError:
            pass
    
    # Apply pagination
    base_query += f" ORDER BY timestamp DESC LIMIT {limit} OFFSET {skip}"
    
    # Execute query
    try:
        # Merge all where conditions
        params = {}
        for condition in where_conditions:
            params.update(condition)
        
        violations_result = db.execute(text(base_query), params)
        violations = violations_result.fetchall()
    except Exception as e:
        logger.error(f"Error getting violations for CSV export: {e}")
        violations = []
    
    # Create CSV content
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow([
        "Violation ID", "Violation Number", "Date", "HOA", "Address", "Location",
        "Resident", "Description", "Summary", "Tags", "Repeat Offender Score",
        "Status", "GPS Coordinates", "Inspected By"
    ])
    
    # Write data
    for violation in violations:
        writer.writerow([
            violation.id,
            violation.violation_number,
            violation.timestamp.strftime("%Y-%m-%d %H:%M:%S") if violation.timestamp else "",
            violation.hoa_name,
            violation.address,
            violation.location,
            violation.offender,
            violation.description,
            violation.summary,
            violation.tags,
            violation.repeat_offender_score,
            violation.status,
            violation.gps_coordinates,
            ""  # We'll need to get username separately if needed
        ])
    
    output.seek(0)
    
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode('utf-8')),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=violations_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"}
    )

@router.put("/{violation_id}", response_model=ViolationOut)
def update_violation(
    violation_id: int,
    updates: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_active_subscription),
):
    """Update a violation (admin and HOA board only)."""
    if current_user.role not in ["admin", "hoa_board"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins and HOA board members can update violations."
        )
    
    violation = db.query(Violation).filter(Violation.id == violation_id).first()
    if not violation:
        raise HTTPException(status_code=404, detail="Violation not found")
    
    # 🔐 RBAC: Check if user can update this violation
    if current_user.role == "hoa_board":
        if current_user.hoa_id is not None:
            user_hoa = db.query(HOA).filter(HOA.id == current_user.hoa_id).first()
            if user_hoa is not None:
                user_hoa_number = f"HOA #{user_hoa.id:03d}"
                if violation.hoa_name != user_hoa_number:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="You can only update violations from your assigned HOA."
                    )
            else:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="No HOA assigned."
                )
    
    # Update allowed fields
    allowed_fields = ['description', 'address', 'location', 'offender', 'tags', 'status']
    for field, value in updates.items():
        if field in allowed_fields and hasattr(violation, field):
            setattr(violation, field, value)
    
    # Add resolution timestamp if marking as resolved
    if 'status' in updates and updates['status'] == "resolved":
        violation.resolved_at = datetime.now(timezone.utc)
        violation.resolved_by = current_user.username
    
    # Add review timestamp if marking as under_review
    if 'status' in updates and updates['status'] == "under_review":
        violation.reviewed_at = datetime.now(timezone.utc)
        violation.reviewed_by = current_user.username
    
    db.commit()
    db.refresh(violation)
    
    return {
        "id": violation.id,
        "violation_number": violation.violation_number,
        "timestamp": violation.timestamp,
        "description": violation.description,
        "summary": violation.summary,
        "tags": violation.tags,
        "repeat_offender_score": violation.repeat_offender_score,
        "hoa_name": violation.hoa_name,
        "address": violation.address,
        "location": violation.location,
        "offender": violation.offender,
        "gps_coordinates": violation.gps_coordinates,
        "status": violation.status,
        "pdf_path": violation.pdf_path,
        "image_url": violation.image_url,
        "user_id": violation.user_id,
        "inspected_by": violation.user.username if violation.user else None,
    }

@router.get("/{violation_id}", response_model=ViolationOut)
def get_violation_by_id(
    violation_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_active_subscription),
):
    """Get a specific violation by ID."""
    violation = db.query(Violation).filter(Violation.id == violation_id).first()
    if not violation:
        raise HTTPException(status_code=404, detail="Violation not found")
    
    # 🔐 RBAC: Check if user can access this violation
    if current_user.role == "admin":
        # Admins can access all violations
        pass
    elif current_user.role in ["inspector", "hoa_board"]:
        # Check if user's HOA matches the violation HOA
        if current_user.hoa_id is not None:
            user_hoa = db.query(HOA).filter(HOA.id == current_user.hoa_id).first()
            if user_hoa is not None:
                # Compare HOA numbers (e.g., "066" vs "066")
                user_hoa_number = f"HOA #{user_hoa.id:03d}"
                if user_hoa_number != violation.hoa_name:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Access denied. You can only view violations from your assigned HOA."
                    )
            else:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="No HOA assigned."
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No HOA assigned."
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied."
        )
    
    return {
        "id": violation.id,
        "violation_number": violation.violation_number,
        "timestamp": violation.timestamp,
        "description": violation.description,
        "summary": violation.summary,
        "tags": violation.tags,
        "repeat_offender_score": violation.repeat_offender_score,
        "hoa_name": violation.hoa_name,
        "address": violation.address,
        "location": violation.location,
        "offender": violation.offender,
        "gps_coordinates": violation.gps_coordinates,
        "status": violation.status,
        "pdf_path": violation.pdf_path,
        "image_url": violation.image_url,
        "user_id": violation.user_id,
        "inspected_by": violation.user.username if violation.user else None,
    }

@router.delete("/{violation_id}")
def delete_violation(
    violation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_active_subscription),
):
    """Delete a violation (admin and HOA board only)."""
    if current_user.role not in ["admin", "hoa_board"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins and HOA board members can delete violations."
        )
    
    violation = db.query(Violation).filter(Violation.id == violation_id).first()
    if not violation:
        raise HTTPException(status_code=404, detail="Violation not found")
    
    # 🔐 RBAC: Check if user can delete this violation
    if current_user.role == "hoa_board":
        if current_user.hoa_id is not None:
            user_hoa = db.query(HOA).filter(HOA.id == current_user.hoa_id).first()
            if user_hoa is not None:
                user_hoa_number = f"HOA #{user_hoa.id:03d}"
                if violation.hoa_name != user_hoa_number:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="You can only delete violations from your assigned HOA."
                    )
            else:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="No HOA assigned."
                )
    
    # Delete associated files
    if violation.pdf_path and os.path.exists(violation.pdf_path):
        try:
            os.remove(violation.pdf_path)
        except Exception as e:
            logger.warning(f"Failed to delete PDF file: {e}")
    
    if violation.image_url and os.path.exists(violation.image_url):
        try:
            os.remove(violation.image_url)
        except Exception as e:
            logger.warning(f"Failed to delete image file: {e}")
    
    # Delete from database
    db.delete(violation)
    db.commit()
    
    return {"message": "Violation deleted successfully"}

@router.get("/{violation_id}/pdf")
def get_violation_pdf(
    violation_id: int,
    user: User = Depends(get_current_user),
    db = Depends(get_db),
):
    """Get PDF for a specific violation."""
    try:
        # Fetch violation from DB
        violation = db.query(Violation).filter(Violation.id == violation_id).first()
        if not violation:
            logger.error(f"Violation {violation_id} not found")
            raise HTTPException(status_code=404, detail="Violation not found")
        
        logger.info(f"PDF request for violation {violation_id}, path: {violation.pdf_path}")
        
        # Check if PDF exists
        if not violation.pdf_path:
            logger.error(f"No PDF path for violation {violation_id}")
            raise HTTPException(status_code=404, detail="PDF not generated for this violation")
        
        if not os.path.exists(violation.pdf_path):
            logger.error(f"PDF file not found at path: {violation.pdf_path}")
            raise HTTPException(status_code=404, detail="PDF file not found on server")
        
        logger.info(f"Serving PDF: {violation.pdf_path}")
        
        # Return PDF file
        return FileResponse(
            violation.pdf_path,
            media_type="application/pdf",
            filename=f"violation_{violation_id}.pdf"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error serving PDF for violation {violation_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.put("/{violation_id}/status")
def update_violation_status(
    violation_id: int,
    new_status: str = Query(...),
    resolution_notes: Optional[str] = Query(None),
    resolved_by: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_active_subscription),
):
    """Update violation status (admin, HOA board, and inspectors only)."""
    
    try:
        # Validate status
        valid_statuses = ["open", "under_review", "resolved", "disputed"]
        if new_status not in valid_statuses:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
            )
        
        # Check permissions
        if current_user.role not in ["admin", "hoa_board", "inspector"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admins, HOA board members, and inspectors can update violation status"
            )
        
        # Create a new session to avoid dependency injection issues
        from database import SessionLocal
        new_db = SessionLocal()
        
        # Test database connection
        try:
            from sqlalchemy import text
            new_db.execute(text("SELECT 1"))
            logger.debug("Database connection test successful")
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            new_db.close()
            raise HTTPException(status_code=500, detail="Database connection failed")
        
        # Get violation with new session
        violation = new_db.query(Violation).filter(Violation.id == violation_id).first()
        if not violation:
            new_db.close()
            raise HTTPException(status_code=404, detail="Violation not found")
        
        # 🔐 RBAC: Check if user can update this violation
        if current_user.role in ["inspector", "hoa_board"]:
            if current_user.hoa_id is not None:
                user_hoa = new_db.query(HOA).filter(HOA.id == current_user.hoa_id).first()
                if user_hoa is not None:
                    user_hoa_number = f"HOA #{user_hoa.id:03d}"
                    if violation.hoa_name != user_hoa_number:
                        new_db.close()
                        raise HTTPException(
                            status_code=status.HTTP_403_FORBIDDEN,
                            detail="You can only update violations from your assigned HOA."
                        )
                else:
                    new_db.close()
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="No HOA assigned."
                    )
        
        # Store old status for logging
        old_status = violation.status
        
        # Update status
        violation.status = new_status
        
        # Add resolution timestamp if marking as resolved
        if new_status == "resolved":
            violation.resolved_at = datetime.now(timezone.utc)
            violation.resolved_by = resolved_by or current_user.username
            violation.resolution_notes = resolution_notes
        
        # Add review timestamp if marking as under_review
        if new_status == "under_review":
            violation.reviewed_at = datetime.now(timezone.utc)
            violation.reviewed_by = current_user.username
        
        new_db.commit()
        # new_db.refresh(violation)  # Temporarily disabled
        
        # Log the status change
        # logger.info(f"Violation {violation_id} status changed from {old_status} to {new_status} by {current_user.username}")
        
        # Send notifications based on status change
        # Status update functionality
        # if new_status == "resolved":
        #     send_resolution_notification(violation, current_user, new_db)
        # elif new_status == "under_review":
        #     send_review_notification(violation, current_user, new_db)
        
        result = {
            "id": violation.id,
            "old_status": old_status,
            "new_status": violation.status,
            "message": f"Violation status updated to {new_status}"
        }
        
        new_db.close()
        return result
        
    except Exception as e:
        print(f"Error in status update: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

@router.put("/{violation_id}/status-simple")
def update_violation_status_simple(
    violation_id: int,
    new_status: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Simple test endpoint without Form parameters."""
    
    try:
        # Get violation
        violation = db.query(Violation).filter(Violation.id == violation_id).first()
        if not violation:
            raise HTTPException(status_code=404, detail="Violation not found")
        
        # Update status
        old_status = violation.status
        violation.status = new_status
        
        db.commit()
        
        return {
            "id": violation.id,
            "old_status": old_status,
            "new_status": violation.status,
            "message": "Status updated successfully"
        }
        
    except Exception as e:
        print(f"Error in simple status update: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

def send_resolution_notification(violation: Violation, user: User, db: Session):
    """Send notification when violation is resolved."""
    try:
        from utils.email_service import email_service
        
        # Get HOA board members to notify
        hoa_board_members = db.query(User).filter(
            User.role == "hoa_board",
            User.hoa_id == user.hoa_id
        ).all()
        
        for member in hoa_board_members:
            if member.email:
                success = email_service.send_resolution_notification(
                    violation=violation,
                    recipient_email=member.email,
                    resolved_by=user.username,
                    resolution_notes=getattr(violation, 'resolution_notes', None)
                )
                if success:
                    logger.info(f"Resolution notification sent to {member.email}")
                else:
                    logger.warning(f"Failed to send resolution notification to {member.email}")
        
    except Exception as e:
        logger.warning(f"Failed to send resolution notification: {e}")

def send_review_notification(violation: Violation, user: User, db: Session):
    """Send notification when violation is under review."""
    try:
        from utils.email_service import email_service
        
        # Get HOA board members to notify
        hoa_board_members = db.query(User).filter(
            User.role == "hoa_board",
            User.hoa_id == user.hoa_id
        ).all()
        
        for member in hoa_board_members:
            if member.email:
                success = email_service.send_escalation_notification(
                    violation=violation,
                    recipient_email=member.email,
                    escalation_reason="Violation escalated for HOA board review"
                )
                if success:
                    logger.info(f"Review notification sent to {member.email}")
                else:
                    logger.warning(f"Failed to send review notification to {member.email}")
        
    except Exception as e:
        logger.warning(f"Failed to send review notification: {e}")

# Letter Generation Models
class LetterRequest(BaseModel):
    letter_content: str

class LetterResponse(BaseModel):
    letter_content: str
    violation_id: int
    generated_by: str
    generated_at: str

# Letter Generation Routes
@router.post("/{violation_id}/generate-letter", response_model=LetterResponse)
def generate_violation_letter(
    violation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_active_subscription),
):
    """Generate a violation letter using GPT based on violation details."""
    try:
        # Get violation details
        violation = db.query(Violation).filter(Violation.id == violation_id).first()
        if not violation:
            raise HTTPException(status_code=404, detail="Violation not found")
        
        # Check if user can access this violation
        if not can_access_hoa(current_user, violation.hoa_name, db):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied. You can only generate letters for violations in your assigned HOA."
            )
        
        # Get HOA details
        hoa = db.query(HOA).filter(HOA.name == violation.hoa_name).first()
        
        # Prepare context for GPT
        violation_date = violation.timestamp.strftime('%B %d, %Y')
        current_date = datetime.now().strftime('%B %d, %Y')
        
        # Create GPT prompt
        prompt = f"""
        Generate a professional HOA violation letter based on the following details:
        
        Violation Information:
        - Violation Number: {violation.violation_number}
        - Date of Violation: {violation_date}
        - Address: {violation.address}
        - Description: {violation.description}
        - Offender: {violation.offender}
        - Status: {violation.status}
        
        HOA Information:
        - HOA Name: {hoa.name if hoa else 'HOA Management'}
        - Contact Email: {hoa.contact_email if hoa else 'hoa@example.com'}
        
        Issuing Officer: {current_user.username}
        Current Date: {current_date}
        
        Please generate a formal, professional letter that:
        1. Clearly states the violation details
        2. Explains the consequences of non-compliance
        3. Provides a deadline for resolution
        4. Includes contact information for questions
        5. Maintains a professional but firm tone
        6. Is formatted as a proper business letter
        
        The letter should be ready to send to the resident.
        """
        
        # Generate letter using GPT (you'll need to configure OpenAI API key)
        try:
            # For now, we'll generate a template letter
            # In production, you would use OpenAI API
            from datetime import timedelta
            
            letter_content = f"""
{current_date}

{hoa.name if hoa else 'HOA Management'}
{hoa.contact_email if hoa else 'hoa@example.com'}

Dear Resident,

RE: Violation Notice - #{violation.violation_number}

This letter serves as official notice of a violation of the HOA community guidelines that was observed on {violation_date} at {violation.address}.

VIOLATION DETAILS:
- Violation Number: {violation.violation_number}
- Date Observed: {violation_date}
- Location: {violation.address}
- Description: {violation.description}
- Current Status: {violation.status.title()}

REQUIRED ACTION:
Please take immediate action to resolve this violation. Failure to address this matter within 14 days of receipt of this notice may result in additional fines and/or further enforcement action as outlined in the HOA bylaws.

COMPLIANCE DEADLINE:
You have until {(datetime.now() + timedelta(days=14)).strftime('%B %d, %Y')} to resolve this violation.

CONTACT INFORMATION:
If you have any questions regarding this violation notice or need assistance in resolving this matter, please contact:

{current_user.username}
HOA Management Team
{hoa.contact_email if hoa else 'hoa@example.com'}

Please include your violation number (#{violation.violation_number}) in all correspondence.

Sincerely,

{current_user.username}
HOA Management Team
{hoa.name if hoa else 'HOA Management'}
            """.strip()
            
        except Exception as e:
            logger.error(f"Failed to generate letter with GPT: {e}")
            # Fallback to template letter
            letter_content = f"""
{current_date}

Dear Resident,

This letter serves as official notice of a violation of the HOA community guidelines that was observed on {violation_date} at {violation.address}.

Violation Number: {violation.violation_number}
Description: {violation.description}

Please take immediate action to resolve this violation within 14 days.

Sincerely,
{current_user.username}
HOA Management Team
            """.strip()
        
        return LetterResponse(
            letter_content=letter_content,
            violation_id=violation_id,
            generated_by=current_user.username,
            generated_at=datetime.now().isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to generate violation letter: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate violation letter")

@router.post("/generate-letter/pdf")
def generate_letter_pdf(
    letter_request: LetterRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_active_subscription),
):
    """Generate a PDF from the letter content."""
    try:
        # Create a styled HTML version of the letter
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>HOA Violation Letter</title>
            <style>
                body {{
                    font-family: 'Times New Roman', serif;
                    font-size: 12pt;
                    line-height: 1.5;
                    margin: 1in;
                    color: #333;
                }}
                .header {{
                    text-align: center;
                    margin-bottom: 2em;
                }}
                .content {{
                    white-space: pre-line;
                    margin-bottom: 2em;
                }}
                .signature {{
                    margin-top: 2em;
                }}
                .footer {{
                    margin-top: 3em;
                    font-size: 10pt;
                    color: #666;
                }}
            </style>
        </head>
        <body>
            <div class="content">
                {letter_request.letter_content.replace(chr(10), '<br>')}
            </div>
            <div class="footer">
                <p>Generated by: {current_user.username}</p>
                <p>Date: {datetime.now().strftime('%B %d, %Y')}</p>
            </div>
        </body>
        </html>
        """
        
        # Generate PDF using the existing PDF utility
        pdf_path = generate_pdf(html_content, f"violation_letter_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")
        
        # Return the PDF file
        return FileResponse(
            path=pdf_path,
            filename=f"violation_letter_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
            media_type="application/pdf"
        )
        
    except Exception as e:
        logger.error(f"Failed to generate letter PDF: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate PDF")
