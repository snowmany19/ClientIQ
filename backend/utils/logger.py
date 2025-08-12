# backend/utils/logger.py

import logging
import sys
import os
from datetime import datetime
from typing import Any, Dict, Optional

# Fallback to standard logging if structlog is not available
try:
    import structlog
    USE_STRUCTLOG = True
except ImportError:
    USE_STRUCTLOG = False

def setup_logging(log_level: str = "INFO", log_file: str = "logs/app.log"):
    """Setup logging for the application."""
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    if USE_STRUCTLOG:
        structlog.configure(
            processors=[
                structlog.stdlib.filter_by_level,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.stdlib.PositionalArgumentsFormatter(),
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.UnicodeDecoder(),
                structlog.processors.JSONRenderer()
            ],
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )
        logging.basicConfig(
            level=getattr(logging, log_level.upper()),
            handlers=[
                logging.StreamHandler(sys.stdout)
            ]
        )
        return structlog.get_logger()
    else:
        logging.basicConfig(
            level=getattr(logging, log_level.upper()),
            handlers=[
                logging.StreamHandler(sys.stdout)
            ]
        )
        # Set formatter for all handlers
        fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        logger = logging.getLogger("contractguard")
        for handler in logger.handlers:
            handler.setFormatter(logging.Formatter(fmt))
        return logger

def get_logger(name: str = "contractguard"):
    """Get a logger instance with the specified name."""
    if USE_STRUCTLOG:
        return structlog.get_logger(name)
    else:
        return logging.getLogger(name)

def log_api_request(
    logger: logging.Logger,
    method: str,
    path: str,
    status_code: int,
    response_time: float,
    user_id: Optional[str] = None,
    ip_address: Optional[str] = None
):
    """Log API request details."""
    extra_data = {
        "method": method,
        "path": path,
        "status_code": status_code,
        "response_time_ms": round(response_time * 1000, 2)
    }
    
    if user_id:
        extra_data["user_id"] = user_id
    if ip_address:
        extra_data["ip_address"] = ip_address
    
    if status_code >= 400:
        logger.warning("API request", **extra_data)
    else:
        logger.info("API request", **extra_data)

def log_error(
    logger: logging.Logger,
    error: Exception,
    context: Optional[Dict[str, Any]] = None,
    user_id: Optional[str] = None
):
    """Log error with context."""
    error_data = {
        "error_type": type(error).__name__,
        "error_message": str(error),
        "user_id": user_id
    }
    
    if context:
        error_data.update(context)
    
    logger.error("Application error", **error_data, exc_info=True)

def log_security_event(
    logger: logging.Logger,
    event_type: str,
    user_id: Optional[str] = None,
    ip_address: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None
):
    """Log security-related events."""
    security_data = {
        "event_type": event_type,
        "user_id": user_id,
        "ip_address": ip_address,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    if details:
        security_data.update(details)
    
    logger.warning("Security event", **security_data)

def log_performance_metric(
    logger: logging.Logger,
    metric_name: str,
    value: float,
    unit: str = "ms",
    context: Optional[Dict[str, Any]] = None
):
    """Log performance metrics."""
    metric_data = {
        "metric_name": metric_name,
        "value": value,
        "unit": unit,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    if context:
        metric_data.update(context)
    
    logger.info("Performance metric", **metric_data)

def log_user_action(
    logger: logging.Logger,
    action: str,
    user_id: str,
    resource_type: Optional[str] = None,
    resource_id: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None
):
    """Log user actions for audit purposes."""
    action_data = {
        "action": action,
        "user_id": user_id,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    if resource_type:
        action_data["resource_type"] = resource_type
    if resource_id:
        action_data["resource_id"] = resource_id
    if details:
        action_data.update(details)
    
    logger.info("User action", **action_data)

def log_contract_analysis(
    logger: logging.Logger,
    contract_id: str,
    analysis_type: str,
    duration: float,
    success: bool,
    user_id: Optional[str] = None,
    error_message: Optional[str] = None
):
    """Log contract analysis events."""
    analysis_data = {
        "contract_id": contract_id,
        "analysis_type": analysis_type,
        "duration_ms": round(duration * 1000, 2),
        "success": success,
        "user_id": user_id,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    if not success and error_message:
        analysis_data["error_message"] = error_message
    
    if success:
        logger.info("Contract analysis completed", **analysis_data)
    else:
        logger.error("Contract analysis failed", **analysis_data)

def log_workspace_activity(
    logger: logging.Logger,
    workspace_id: str,
    activity_type: str,
    user_id: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None
):
    """Log workspace-related activities."""
    activity_data = {
        "workspace_id": workspace_id,
        "activity_type": activity_type,
        "user_id": user_id,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    if details:
        activity_data.update(details)
    
    logger.info("Workspace activity", **activity_data)

def log_system_health(
    logger: logging.Logger,
    component: str,
    status: str,
    metrics: Optional[Dict[str, Any]] = None,
    error_message: Optional[str] = None
):
    """Log system health and status information."""
    health_data = {
        "component": component,
        "status": status,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    if metrics:
        health_data.update(metrics)
    if error_message:
        health_data["error_message"] = error_message
    
    if status == "healthy":
        logger.info("System health check", **health_data)
    elif status == "warning":
        logger.warning("System health warning", **health_data)
    else:
        logger.error("System health error", **health_data) 