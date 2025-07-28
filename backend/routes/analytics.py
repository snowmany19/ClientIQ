# backend/routes/analytics.py

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, extract
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from database import get_db
from models import Violation, User, HOA, Resident
from utils.auth_utils import get_current_user, require_active_subscription
from utils.logger import get_logger

router = APIRouter(prefix="/analytics", tags=["Analytics"])
logger = get_logger("analytics")

@router.get("/dashboard-metrics")
def get_dashboard_metrics(
    hoa_id: Optional[int] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_active_subscription),
):
    """Get comprehensive dashboard metrics."""
    from sqlalchemy import text
    
    try:
        # Build base query and conditions
        base_conditions = []
        params = {}
        
        if hoa_id:
            base_conditions.append("hoa_id = :hoa_id")
            params["hoa_id"] = hoa_id
        
        if start_date:
            start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            base_conditions.append("timestamp >= :start_date")
            params["start_date"] = start_dt
        
        if end_date:
            end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            base_conditions.append("timestamp <= :end_date")
            params["end_date"] = end_dt
        
        where_clause = " AND ".join(base_conditions) if base_conditions else "1=1"
        
        # Get total violations
        total_query = f"SELECT COUNT(*) FROM violations WHERE {where_clause}"
        total_violations = db.execute(text(total_query), params).scalar()
        
        # Get violations by status
        status_query = f"""
            SELECT status, COUNT(*) as count 
            FROM violations 
            WHERE {where_clause}
            GROUP BY status
        """
        status_result = db.execute(text(status_query), params)
        status_counts = [(row.status, row.count) for row in status_result]
        
        # Get violations by repeat offender score
        score_query = f"""
            SELECT repeat_offender_score, COUNT(*) as count 
            FROM violations 
            WHERE {where_clause}
            GROUP BY repeat_offender_score
        """
        score_result = db.execute(text(score_query), params)
        score_counts = [(row.repeat_offender_score, row.count) for row in score_result]
        
        # Get average repeat offender score
        avg_query = f"SELECT AVG(repeat_offender_score) FROM violations WHERE {where_clause}"
        avg_score = db.execute(text(avg_query), params).scalar()
        
        # Get violations by month (last 12 months)
        monthly_query = f"""
            SELECT 
                EXTRACT(YEAR FROM timestamp) as year,
                EXTRACT(MONTH FROM timestamp) as month,
                COUNT(*) as count
            FROM violations 
            WHERE {where_clause}
            GROUP BY EXTRACT(YEAR FROM timestamp), EXTRACT(MONTH FROM timestamp)
            ORDER BY year DESC, month DESC
            LIMIT 12
        """
        monthly_result = db.execute(text(monthly_query), params)
        monthly_data = [(row.year, row.month, row.count) for row in monthly_result]
        
        # Get top problem areas (addresses)
        problem_query = f"""
            SELECT address, COUNT(*) as count
            FROM violations 
            WHERE {where_clause}
            GROUP BY address
            ORDER BY count DESC
            LIMIT 10
        """
        problem_result = db.execute(text(problem_query), params)
        problem_areas = [(row.address, row.count) for row in problem_result]
        
        # Get top repeat offenders
        offender_query = f"""
            SELECT 
                offender, 
                COUNT(*) as count,
                AVG(repeat_offender_score) as avg_score
            FROM violations 
            WHERE {where_clause}
            GROUP BY offender
            ORDER BY count DESC
            LIMIT 10
        """
        offender_result = db.execute(text(offender_query), params)
        repeat_offenders = [(row.offender, row.count, row.avg_score) for row in offender_result]
        
        return {
            "total_violations": total_violations,
            "status_breakdown": {status: count for status, count in status_counts},
            "score_breakdown": {score: count for score, count in score_counts},
            "average_repeat_offender_score": float(avg_score) if avg_score else 0,
            "monthly_trends": [
                {
                    "year": int(year),
                    "month": int(month),
                    "count": int(count)
                } for year, month, count in monthly_data
            ],
            "problem_areas": [
                {
                    "address": address,
                    "count": int(count)
                } for address, count in problem_areas
            ],
            "repeat_offenders": [
                {
                    "offender": offender,
                    "count": int(count),
                    "average_score": float(avg_score) if avg_score else 0
                } for offender, count, avg_score in repeat_offenders
            ]
        }
    except Exception as e:
        logger.error(f"Error getting dashboard metrics: {e}")
        return {
            "total_violations": 0,
            "status_breakdown": {},
            "score_breakdown": {},
            "average_repeat_offender_score": 0,
            "monthly_trends": [],
            "problem_areas": [],
            "repeat_offenders": []
        }

@router.get("/violation-heatmap")
def get_violation_heatmap(
    hoa_id: Optional[int] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_active_subscription),
):
    """Get violation heatmap data with GPS coordinates."""
    try:
        # Build query filters
        query_filters = [Violation.gps_coordinates.isnot(None)]
        if hoa_id:
            query_filters.append(Violation.hoa_id == hoa_id)
        
        if start_date:
            start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            query_filters.append(Violation.timestamp >= start_dt)
        
        if end_date:
            end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            query_filters.append(Violation.timestamp <= end_dt)
        
        # Get violations with GPS coordinates
        violations = db.query(
            Violation.gps_coordinates,
            Violation.address,
            Violation.repeat_offender_score,
            func.count(Violation.id).label('count')
        ).filter(*query_filters).group_by(
            Violation.gps_coordinates,
            Violation.address,
            Violation.repeat_offender_score
        ).all()
        
        heatmap_data = []
        for coords, address, score, count in violations:
            if coords and ',' in coords:
                try:
                    lat, lon = map(float, coords.split(','))
                    heatmap_data.append({
                        "latitude": lat,
                        "longitude": lon,
                        "address": address,
                        "repeat_offender_score": score,
                        "violation_count": int(count),
                        "intensity": int(count) * (score or 1)  # Weight by score
                    })
                except ValueError:
                    continue
        
        return {
            "heatmap_data": heatmap_data,
            "total_points": len(heatmap_data)
        }
        
    except Exception as e:
        logger.error(f"Failed to get violation heatmap: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve heatmap data"
        )

@router.get("/trend-analysis")
def get_trend_analysis(
    hoa_id: Optional[int] = None,
    period: str = Query("monthly", description="Analysis period: daily, weekly, monthly, yearly"),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_active_subscription),
):
    """Get trend analysis for violations."""
    try:
        # Build query filters
        query_filters = []
        if hoa_id:
            query_filters.append(Violation.hoa_id == hoa_id)
        
        if start_date:
            start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            query_filters.append(Violation.timestamp >= start_dt)
        
        if end_date:
            end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            query_filters.append(Violation.timestamp <= end_dt)
        
        # Determine time grouping based on period
        if period == "daily":
            time_group = func.date(Violation.timestamp)
            time_label = "date"
        elif period == "weekly":
            time_group = func.date_trunc('week', Violation.timestamp)
            time_label = "week"
        elif period == "monthly":
            time_group = func.date_trunc('month', Violation.timestamp)
            time_label = "month"
        elif period == "yearly":
            time_group = func.date_trunc('year', Violation.timestamp)
            time_label = "year"
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid period. Must be daily, weekly, monthly, or yearly"
            )
        
        # Get trend data
        trend_data = db.query(
            time_group.label('time_period'),
            func.count(Violation.id).label('violation_count'),
            func.avg(Violation.repeat_offender_score).label('avg_score'),
            func.count(Violation.id).filter(Violation.status == "open").label('open_count'),
            func.count(Violation.id).filter(Violation.status == "resolved").label('resolved_count'),
            func.count(Violation.id).filter(Violation.status == "disputed").label('disputed_count')
        ).filter(*query_filters).group_by(time_group).order_by(time_group).all()
        
        # Calculate trend indicators
        if len(trend_data) >= 2:
            recent_count = trend_data[-1].violation_count
            previous_count = trend_data[-2].violation_count
            trend_direction = "increasing" if recent_count > previous_count else "decreasing" if recent_count < previous_count else "stable"
            trend_percentage = ((recent_count - previous_count) / previous_count * 100) if previous_count > 0 else 0
        else:
            trend_direction = "insufficient_data"
            trend_percentage = 0
        
        return {
            "period": period,
            "trend_direction": trend_direction,
            "trend_percentage": round(trend_percentage, 2),
            "data": [
                {
                    "time_period": str(row.time_period),
                    "violation_count": int(row.violation_count),
                    "average_score": float(row.avg_score) if row.avg_score else 0,
                    "open_count": int(row.open_count),
                    "resolved_count": int(row.resolved_count),
                    "disputed_count": int(row.disputed_count)
                } for row in trend_data
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get trend analysis: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve trend analysis"
        )

@router.get("/compliance-analysis")
def get_compliance_analysis(
    hoa_id: Optional[int] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_active_subscription),
):
    """Get compliance analysis and effectiveness metrics."""
    try:
        # Build query filters
        query_filters = []
        if hoa_id:
            query_filters.append(Violation.hoa_id == hoa_id)
        
        if start_date:
            start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            query_filters.append(Violation.timestamp >= start_dt)
        
        if end_date:
            end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            query_filters.append(Violation.timestamp <= end_dt)
        
        # Get total violations
        total_violations = db.query(func.count(Violation.id)).filter(*query_filters).scalar()
        
        # Get resolved violations
        resolved_violations = db.query(func.count(Violation.id)).filter(
            *query_filters,
            Violation.status == "resolved"
        ).scalar()
        
        # Get disputed violations
        disputed_violations = db.query(func.count(Violation.id)).filter(
            *query_filters,
            Violation.status == "disputed"
        ).scalar()
        
        # Get open violations
        open_violations = db.query(func.count(Violation.id)).filter(
            *query_filters,
            Violation.status == "open"
        ).scalar()
        
        # Calculate compliance rates
        resolution_rate = (resolved_violations / total_violations * 100) if total_violations > 0 else 0
        dispute_rate = (disputed_violations / total_violations * 100) if total_violations > 0 else 0
        open_rate = (open_violations / total_violations * 100) if total_violations > 0 else 0
        
        # Get average resolution time
        resolution_time_data = db.query(
            func.avg(
                func.extract('epoch', Violation.resolved_at - Violation.timestamp) / 86400
            )
        ).filter(
            *query_filters,
            Violation.status == "resolved",
            Violation.resolved_at.isnot(None)
        ).scalar()
        
        avg_resolution_days = float(resolution_time_data) if resolution_time_data else 0
        
        # Get repeat offender analysis
        repeat_offender_data = db.query(
            Violation.offender,
            func.count(Violation.id).label('count')
        ).filter(*query_filters).group_by(Violation.offender).having(
            func.count(Violation.id) > 1
        ).all()
        
        repeat_offender_count = len(repeat_offender_data)
        repeat_offender_rate = (repeat_offender_count / total_violations * 100) if total_violations > 0 else 0
        
        return {
            "total_violations": total_violations,
            "resolved_violations": resolved_violations,
            "disputed_violations": disputed_violations,
            "open_violations": open_violations,
            "resolution_rate": round(resolution_rate, 2),
            "dispute_rate": round(dispute_rate, 2),
            "open_rate": round(open_rate, 2),
            "average_resolution_days": round(avg_resolution_days, 1),
            "repeat_offender_count": repeat_offender_count,
            "repeat_offender_rate": round(repeat_offender_rate, 2),
            "compliance_score": round(resolution_rate - dispute_rate, 2)
        }
        
    except Exception as e:
        logger.error(f"Failed to get compliance analysis: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve compliance analysis"
        )

@router.get("/predictive-insights")
def get_predictive_insights(
    hoa_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_active_subscription),
):
    """Get predictive insights and recommendations."""
    try:
        # Build query filters
        query_filters = []
        if hoa_id:
            query_filters.append(Violation.hoa_id == hoa_id)
        
        # Get recent violations (last 90 days)
        recent_date = datetime.utcnow() - timedelta(days=90)
        recent_violations = db.query(func.count(Violation.id)).filter(
            *query_filters,
            Violation.timestamp >= recent_date
        ).scalar()
        
        # Get previous period violations (90-180 days ago)
        previous_start = datetime.utcnow() - timedelta(days=180)
        previous_end = datetime.utcnow() - timedelta(days=90)
        previous_violations = db.query(func.count(Violation.id)).filter(
            *query_filters,
            Violation.timestamp >= previous_start,
            Violation.timestamp < previous_end
        ).scalar()
        
        # Calculate trend
        trend_percentage = ((recent_violations - previous_violations) / previous_violations * 100) if previous_violations > 0 else 0
        
        # Get seasonal patterns
        seasonal_data = db.query(
            extract('month', Violation.timestamp).label('month'),
            func.count(Violation.id).label('count')
        ).filter(*query_filters).group_by(
            extract('month', Violation.timestamp)
        ).all()
        
        # Find peak months
        peak_months = sorted(seasonal_data, key=lambda x: x.count, reverse=True)[:3]
        
        # Get problem areas
        problem_areas = db.query(
            Violation.address,
            func.count(Violation.id).label('count')
        ).filter(*query_filters).group_by(Violation.address).order_by(
            func.count(Violation.id).desc()
        ).limit(5).all()
        
        # Generate insights
        insights = []
        
        if trend_percentage > 20:
            insights.append({
                "type": "warning",
                "title": "Increasing Violation Trend",
                "description": f"Violations have increased by {abs(trend_percentage):.1f}% in the last 90 days",
                "recommendation": "Consider increasing patrol frequency or implementing stricter enforcement"
            })
        elif trend_percentage < -20:
            insights.append({
                "type": "positive",
                "title": "Improving Compliance",
                "description": f"Violations have decreased by {abs(trend_percentage):.1f}% in the last 90 days",
                "recommendation": "Current enforcement strategies are working well"
            })
        
        if peak_months:
            peak_month_names = [get_month_name(month) for month, _ in peak_months]
            insights.append({
                "type": "info",
                "title": "Seasonal Patterns",
                "description": f"Peak violation months: {', '.join(peak_month_names)}",
                "recommendation": "Increase monitoring during peak months"
            })
        
        if problem_areas:
            insights.append({
                "type": "warning",
                "title": "Problem Areas Identified",
                "description": f"Top problem area: {problem_areas[0].address} with {problem_areas[0].count} violations",
                "recommendation": "Focus enforcement efforts on identified problem areas"
            })
        
        return {
            "trend_percentage": round(trend_percentage, 1),
            "trend_direction": "increasing" if trend_percentage > 0 else "decreasing" if trend_percentage < 0 else "stable",
            "recent_violations": recent_violations,
            "previous_violations": previous_violations,
            "peak_months": [
                {
                    "month": get_month_name(month),
                    "violation_count": int(count)
                } for month, count in peak_months
            ],
            "problem_areas": [
                {
                    "address": address,
                    "violation_count": int(count)
                } for address, count in problem_areas
            ],
            "insights": insights
        }
        
    except Exception as e:
        logger.error(f"Failed to get predictive insights: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve predictive insights"
        )

def get_month_name(month_number: int) -> str:
    """Convert month number to month name."""
    months = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]
    return months[month_number - 1] if 1 <= month_number <= 12 else "Unknown" 