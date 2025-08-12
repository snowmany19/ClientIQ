# backend/routes/analytics.py

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, extract, text
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from database import get_db
from models import ContractRecord, User, Workspace, AnalyticsEvent
from utils.auth_utils import get_current_user, require_active_subscription
from utils.logger import get_logger
from schemas import DashboardMetrics

router = APIRouter(tags=["Analytics"])
logger = get_logger("analytics")

@router.get("/dashboard-metrics", response_model=DashboardMetrics)
def get_dashboard_metrics(
    workspace_id: Optional[int] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_active_subscription),
):
    """Get comprehensive dashboard metrics for ContractGuard.ai."""
    try:
        # Build base query and conditions
        base_conditions = []
        params = {}
        
        # Note: workspace_id filtering is disabled since contract_records table doesn't have workspace_id column
        # if workspace_id:
        #     base_conditions.append("workspace_id = :workspace_id")
        #     params["workspace_id"] = workspace_id
        # elif current_user.workspace_id:
        #     base_conditions.append("workspace_id = :workspace_id")
        #     params["workspace_id"] = current_user.workspace_id
        
        if start_date:
            start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            base_conditions.append("created_at >= :start_date")
            params["start_date"] = start_dt
        
        if end_date:
            end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            base_conditions.append("created_at <= :end_date")
            params["end_date"] = end_dt
        
        where_clause = " AND ".join(base_conditions) if base_conditions else "1=1"
        
        # Get total contracts
        total_query = f"SELECT COUNT(*) FROM contract_records WHERE {where_clause}"
        total_contracts = db.execute(text(total_query), params).scalar()
        
        # Get contracts by status
        status_query = f"""
            SELECT status, COUNT(*) as count 
            FROM contract_records 
            WHERE {where_clause}
            GROUP BY status
        """
        status_result = db.execute(text(status_query), params)
        status_counts = [(row.status, row.count) for row in status_result]
        
        # Calculate status-specific counts
        status_dict = {status: count for status, count in status_counts}
        pending_contracts = status_dict.get('pending', 0)
        analyzed_contracts = status_dict.get('analyzed', 0)
        reviewed_contracts = status_dict.get('reviewed', 0)
        approved_contracts = status_dict.get('approved', 0)
        rejected_contracts = status_dict.get('rejected', 0)
        
        # Get high risk contracts (contracts with risk items)
        risk_query = f"""
            SELECT COUNT(*) 
            FROM contract_records 
            WHERE {where_clause} 
            AND risk_items IS NOT NULL 
            AND json_array_length(risk_items) > 0
        """
        high_risk_contracts = db.execute(text(risk_query), params).scalar()
        
        # Get contracts by month (last 12 months)
        monthly_query = f"""
            SELECT 
                EXTRACT(YEAR FROM created_at) as year,
                EXTRACT(MONTH FROM created_at) as month,
                COUNT(*) as count
            FROM contract_records 
            WHERE {where_clause}
            GROUP BY EXTRACT(YEAR FROM created_at), EXTRACT(MONTH FROM created_at)
            ORDER BY year DESC, month DESC
            LIMIT 12
        """
        monthly_result = db.execute(text(monthly_query), params)
        monthly_data = [(row.year, row.month, row.count) for row in monthly_result]
        
        # Format monthly trends for frontend
        monthly_trends = []
        for year, month, count in monthly_data:
            month_name = get_month_name(int(month))
            date_str = f"{int(year)}-{int(month):02d}-01"
            monthly_trends.append({
                "date": date_str,
                "count": count
            })
        
        # Get top contract categories
        category_query = f"""
            SELECT category, COUNT(*) as count 
            FROM contract_records 
            WHERE {where_clause}
            GROUP BY category 
            ORDER BY count DESC 
            LIMIT 5
        """
        category_result = db.execute(text(category_query), params)
        top_categories = [
            {"category": row.category, "count": row.count} 
            for row in category_result
        ]
        
        # Calculate average analysis time (placeholder - would need actual analysis timestamps)
        average_analysis_time = 2.5  # Placeholder in hours
        
        return DashboardMetrics(
            total_contracts=total_contracts or 0,
            analyzed_contracts=analyzed_contracts or 0,
            pending_contracts=pending_contracts or 0,
            high_risk_contracts=high_risk_contracts or 0,
            monthly_contract_trends=monthly_trends,
            top_contract_categories=top_categories,
            average_analysis_time=average_analysis_time
        )
        
    except Exception as e:
        logger.error(f"Error getting dashboard metrics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve dashboard metrics"
        )

@router.get("/contract-analytics")
def get_contract_analytics(
    workspace_id: Optional[int] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_active_subscription),
):
    """Get detailed contract analytics."""
    try:
        # Build base conditions
        base_conditions = []
        params = {}
        
        if workspace_id:
            base_conditions.append("workspace_id = :workspace_id")
            params["workspace_id"] = workspace_id
        elif current_user.workspace_id:
            base_conditions.append("workspace_id = :workspace_id")
            params["workspace_id"] = current_user.workspace_id
        
        if start_date:
            start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            base_conditions.append("created_at >= :start_date")
            params["start_date"] = start_dt
        
        if end_date:
            end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            base_conditions.append("created_at <= :end_date")
            params["end_date"] = end_dt
        
        where_clause = " AND ".join(base_conditions) if base_conditions else "1=1"
        
        # Get contracts by category distribution
        category_query = f"""
            SELECT category, COUNT(*) as count 
            FROM contract_records 
            WHERE {where_clause}
            GROUP BY category
        """
        category_result = db.execute(text(category_query), params)
        category_distribution = [
            {"category": row.category, "count": row.count} 
            for row in category_result
        ]
        
        # Get contracts by counterparty (top 10)
        counterparty_query = f"""
            SELECT counterparty, COUNT(*) as count 
            FROM contract_records 
            WHERE {where_clause}
            GROUP BY counterparty 
            ORDER BY count DESC 
            LIMIT 10
        """
        counterparty_result = db.execute(text(counterparty_query), params)
        top_counterparties = [
            {"counterparty": row.counterparty, "count": row.count} 
            for row in counterparty_result
        ]
        
        # Get risk analysis summary
        risk_query = f"""
            SELECT 
                COUNT(*) as total_contracts,
                COUNT(CASE WHEN risk_items IS NOT NULL AND jsonb_array_length(risk_items) > 0 THEN 1 END) as contracts_with_risks,
                COUNT(CASE WHEN rewrite_suggestions IS NOT NULL AND jsonb_array_length(rewrite_suggestions) > 0 THEN 1 END) as contracts_with_suggestions
            FROM contract_records 
            WHERE {where_clause}
        """
        risk_result = db.execute(text(risk_query), params).fetchone()
        
        risk_summary = {
            "total_contracts": risk_result.total_contracts or 0,
            "contracts_with_risks": risk_result.contracts_with_risks or 0,
            "contracts_with_suggestions": risk_result.contracts_with_suggestions or 0
        }
        
        return {
            "category_distribution": category_distribution,
            "top_counterparties": top_counterparties,
            "risk_summary": risk_summary
        }
        
    except Exception as e:
        logger.error(f"Error getting contract analytics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve contract analytics"
        )

@router.get("/user-activity")
def get_user_activity(
    workspace_id: Optional[int] = None,
    days: int = Query(30, description="Number of days to analyze"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_active_subscription),
):
    """Get user activity analytics."""
    try:
        # Build base conditions
        base_conditions = []
        params = {}
        
        if workspace_id:
            base_conditions.append("workspace_id = :workspace_id")
            params["workspace_id"] = workspace_id
        elif current_user.workspace_id:
            base_conditions.append("workspace_id = :workspace_id")
            params["workspace_id"] = current_user.workspace_id
        
        # Get date range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        base_conditions.append("timestamp >= :start_date")
        base_conditions.append("timestamp <= :end_date")
        params["start_date"] = start_date
        params["end_date"] = end_date
        
        where_clause = " AND ".join(base_conditions)
        
        # Get user activity by event type
        activity_query = f"""
            SELECT 
                event_type,
                COUNT(*) as count,
                COUNT(DISTINCT user_id) as unique_users
            FROM analytics_events 
            WHERE {where_clause}
            GROUP BY event_type
            ORDER BY count DESC
        """
        activity_result = db.execute(text(activity_query), params)
        activity_summary = [
            {
                "event_type": row.event_type,
                "count": row.count,
                "unique_users": row.unique_users
            }
            for row in activity_result
        ]
        
        # Get daily activity trends
        daily_query = f"""
            SELECT 
                DATE(timestamp) as date,
                COUNT(*) as count
            FROM analytics_events 
            WHERE {where_clause}
            GROUP BY DATE(timestamp)
            ORDER BY date
        """
        daily_result = db.execute(text(daily_query), params)
        daily_trends = [
            {
                "date": row.date.isoformat(),
                "count": row.count
            }
            for row in daily_result
        ]
        
        return {
            "activity_summary": activity_summary,
            "daily_trends": daily_trends,
            "period_days": days
        }
        
    except Exception as e:
        logger.error(f"Error getting user activity: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user activity analytics"
        )

@router.get("/workspace-insights")
def get_workspace_insights(
    workspace_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_active_subscription),
):
    """Get workspace-specific insights."""
    try:
        # Use current user's workspace if none specified
        if not workspace_id:
            workspace_id = current_user.workspace_id
        
        if not workspace_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No workspace specified"
            )
        
        # Get workspace information
        workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
        if not workspace:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workspace not found"
            )
        
        # Get user count in workspace
        # Note: workspace_id filtering is disabled since users table may not have workspace_id column
        user_count = db.query(User).count()
        
        # Get contract count in workspace
        # Note: ContractRecord table doesn't have workspace_id column, so we'll count all contracts for now
        contract_count = db.query(ContractRecord).count()
        
        # Get recent activity
        # Note: workspace_id filtering is disabled since analytics_events table may not have workspace_id column
        recent_activity = db.query(AnalyticsEvent).order_by(AnalyticsEvent.timestamp.desc()).limit(10).all()
        
        activity_summary = [
            {
                "event_type": event.event_type,
                "timestamp": event.timestamp.isoformat(),
                "user_id": event.user_id
            }
            for event in recent_activity
        ]
        
        return {
            "workspace": {
                "id": workspace.id,
                "name": workspace.name,
                "company_name": workspace.company_name,
                "industry": workspace.industry
            },
            "user_count": user_count,
            "contract_count": contract_count,
            "recent_activity": activity_summary
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting workspace insights: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve workspace insights"
        )

def get_month_name(month_number: int) -> str:
    """Convert month number to month name."""
    month_names = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]
    return month_names[month_number - 1] if 1 <= month_number <= 12 else "Unknown" 