import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
from typing import Optional, List, Dict, Any
from jinja2 import Template
from utils.logger import get_logger

logger = get_logger("email_alerts")

# Email templates
EMAIL_TEMPLATES = {
    "new_violation": """
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
            .container { max-width: 600px; margin: 0 auto; padding: 20px; }
            .header { background: #3b82f6; color: white; padding: 20px; text-align: center; }
            .content { padding: 20px; background: #f9fafb; }
            .footer { text-align: center; padding: 20px; color: #666; font-size: 12px; }
            .violation-details { background: white; padding: 15px; margin: 15px 0; border-left: 4px solid #3b82f6; }
            .button { display: inline-block; padding: 10px 20px; background: #3b82f6; color: white; text-decoration: none; border-radius: 5px; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🚨 New HOA Violation Reported</h1>
            </div>
            <div class="content">
                <p>Hello {{ user_name }},</p>
                <p>A new violation has been reported in your HOA community.</p>
                
                <div class="violation-details">
                    <h3>Violation Details:</h3>
                    <p><strong>Violation #:</strong> {{ violation_number }}</p>
                    <p><strong>Description:</strong> {{ description }}</p>
                    <p><strong>Address:</strong> {{ address }}</p>
                    <p><strong>Location:</strong> {{ location }}</p>
                    <p><strong>Reported:</strong> {{ timestamp }}</p>
                    <p><strong>Status:</strong> {{ status }}</p>
                </div>
                
                <p>Please review this violation and take appropriate action.</p>
                
                <a href="{{ dashboard_url }}" class="button">View in Dashboard</a>
            </div>
            <div class="footer">
                <p>This is an automated notification from CivicLogHOA</p>
                <p>© {{ current_year }} CivicLogHOA. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """,
    
    "violation_resolved": """
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
            .container { max-width: 600px; margin: 0 auto; padding: 20px; }
            .header { background: #10b981; color: white; padding: 20px; text-align: center; }
            .content { padding: 20px; background: #f9fafb; }
            .footer { text-align: center; padding: 20px; color: #666; font-size: 12px; }
            .violation-details { background: white; padding: 15px; margin: 15px 0; border-left: 4px solid #10b981; }
            .button { display: inline-block; padding: 10px 20px; background: #10b981; color: white; text-decoration: none; border-radius: 5px; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>✅ Violation Resolved</h1>
            </div>
            <div class="content">
                <p>Hello {{ user_name }},</p>
                <p>A violation has been marked as resolved in your HOA community.</p>
                
                <div class="violation-details">
                    <h3>Violation Details:</h3>
                    <p><strong>Violation #:</strong> {{ violation_number }}</p>
                    <p><strong>Description:</strong> {{ description }}</p>
                    <p><strong>Address:</strong> {{ address }}</p>
                    <p><strong>Resolved By:</strong> {{ resolved_by }}</p>
                    <p><strong>Resolution Notes:</strong> {{ resolution_notes }}</p>
                    <p><strong>Resolved:</strong> {{ timestamp }}</p>
                </div>
                
                <a href="{{ dashboard_url }}" class="button">View in Dashboard</a>
            </div>
            <div class="footer">
                <p>This is an automated notification from CivicLogHOA</p>
                <p>© {{ current_year }} CivicLogHOA. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """,
    
    "monthly_report": """
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
            .container { max-width: 600px; margin: 0 auto; padding: 20px; }
            .header { background: #6366f1; color: white; padding: 20px; text-align: center; }
            .content { padding: 20px; background: #f9fafb; }
            .footer { text-align: center; padding: 20px; color: #666; font-size: 12px; }
            .stats { background: white; padding: 15px; margin: 15px 0; border-left: 4px solid #6366f1; }
            .button { display: inline-block; padding: 10px 20px; background: #6366f1; color: white; text-decoration: none; border-radius: 5px; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>📊 Monthly HOA Report</h1>
            </div>
            <div class="content">
                <p>Hello {{ user_name }},</p>
                <p>Here's your monthly HOA violation report for {{ month_year }}.</p>
                
                <div class="stats">
                    <h3>Monthly Statistics:</h3>
                    <p><strong>Total Violations:</strong> {{ total_violations }}</p>
                    <p><strong>New Violations:</strong> {{ new_violations }}</p>
                    <p><strong>Resolved Violations:</strong> {{ resolved_violations }}</p>
                    <p><strong>Pending Violations:</strong> {{ pending_violations }}</p>
                    <p><strong>Response Rate:</strong> {{ response_rate }}%</p>
                </div>
                
                <p>Keep up the great work maintaining our community standards!</p>
                
                <a href="{{ dashboard_url }}" class="button">View Full Report</a>
            </div>
            <div class="footer">
                <p>This is an automated notification from CivicLogHOA</p>
                <p>© {{ current_year }} CivicLogHOA. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """,
    
    "security_alert": """
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
            .container { max-width: 600px; margin: 0 auto; padding: 20px; }
            .header { background: #ef4444; color: white; padding: 20px; text-align: center; }
            .content { padding: 20px; background: #f9fafb; }
            .footer { text-align: center; padding: 20px; color: #666; font-size: 12px; }
            .alert-details { background: white; padding: 15px; margin: 15px 0; border-left: 4px solid #ef4444; }
            .button { display: inline-block; padding: 10px 20px; background: #ef4444; color: white; text-decoration: none; border-radius: 5px; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🔒 Security Alert</h1>
            </div>
            <div class="content">
                <p>Hello {{ user_name }},</p>
                <p>We detected a security event on your account.</p>
                
                <div class="alert-details">
                    <h3>Security Event Details:</h3>
                    <p><strong>Event Type:</strong> {{ event_type }}</p>
                    <p><strong>Location:</strong> {{ location }}</p>
                    <p><strong>Device:</strong> {{ device }}</p>
                    <p><strong>Time:</strong> {{ timestamp }}</p>
                    <p><strong>IP Address:</strong> {{ ip_address }}</p>
                </div>
                
                <p>If this wasn't you, please secure your account immediately.</p>
                
                <a href="{{ security_url }}" class="button">Review Security Settings</a>
            </div>
            <div class="footer">
                <p>This is an automated notification from CivicLogHOA</p>
                <p>© {{ current_year }} CivicLogHOA. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """
}

class EmailAlertService:
    def __init__(self):
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_username = os.getenv("SMTP_USERNAME")
        self.smtp_password = os.getenv("SMTP_PASSWORD")
        self.from_email = os.getenv("FROM_EMAIL", "noreply@civicloghoa.com")
        self.app_url = os.getenv("APP_URL", "http://localhost:3000")
        
    def send_email(
        self,
        to_email: str,
        subject: str,
        template_name: str,
        template_data: Dict[str, Any],
        attachment_path: Optional[str] = None
    ) -> bool:
        """Send an email using a template"""
        try:
            if not self.smtp_username or not self.smtp_password:
                logger.warning("SMTP credentials not configured, skipping email send")
                return False
                
            # Get template
            template_html = EMAIL_TEMPLATES.get(template_name)
            if not template_html:
                logger.error(f"Email template '{template_name}' not found")
                return False
                
            # Render template
            template = Template(template_html)
            html_content = template.render(
                **template_data,
                current_year=datetime.now().year,
                dashboard_url=f"{self.app_url}/dashboard",
                security_url=f"{self.app_url}/dashboard/settings"
            )
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = self.from_email
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Add HTML content
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)
            
            # Add attachment if provided
            if attachment_path and os.path.exists(attachment_path):
                with open(attachment_path, "rb") as attachment:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(attachment.read())
                    
                encoders.encode_base64(part)
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename= {os.path.basename(attachment_path)}'
                )
                msg.attach(part)
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
                
            logger.info(f"Email sent successfully to {to_email}: {subject}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return False
    
    def send_violation_notification(
        self,
        user_email: str,
        user_name: str,
        violation_data: Dict[str, Any]
    ) -> bool:
        """Send new violation notification"""
        return self.send_email(
            to_email=user_email,
            subject=f"New HOA Violation - #{violation_data.get('violation_number', 'N/A')}",
            template_name="new_violation",
            template_data={
                "user_name": user_name,
                "violation_number": violation_data.get('violation_number', 'N/A'),
                "description": violation_data.get('description', ''),
                "address": violation_data.get('address', ''),
                "location": violation_data.get('location', ''),
                "timestamp": violation_data.get('timestamp', ''),
                "status": violation_data.get('status', 'New')
            }
        )
    
    def send_violation_resolved_notification(
        self,
        user_email: str,
        user_name: str,
        violation_data: Dict[str, Any]
    ) -> bool:
        """Send violation resolved notification"""
        return self.send_email(
            to_email=user_email,
            subject=f"Violation Resolved - #{violation_data.get('violation_number', 'N/A')}",
            template_name="violation_resolved",
            template_data={
                "user_name": user_name,
                "violation_number": violation_data.get('violation_number', 'N/A'),
                "description": violation_data.get('description', ''),
                "address": violation_data.get('address', ''),
                "resolved_by": violation_data.get('resolved_by', ''),
                "resolution_notes": violation_data.get('resolution_notes', ''),
                "timestamp": violation_data.get('timestamp', '')
            }
        )
    
    def send_monthly_report(
        self,
        user_email: str,
        user_name: str,
        report_data: Dict[str, Any]
    ) -> bool:
        """Send monthly report notification"""
        return self.send_email(
            to_email=user_email,
            subject=f"Monthly HOA Report - {report_data.get('month_year', '')}",
            template_name="monthly_report",
            template_data={
                "user_name": user_name,
                "month_year": report_data.get('month_year', ''),
                "total_violations": report_data.get('total_violations', 0),
                "new_violations": report_data.get('new_violations', 0),
                "resolved_violations": report_data.get('resolved_violations', 0),
                "pending_violations": report_data.get('pending_violations', 0),
                "response_rate": report_data.get('response_rate', 0)
            }
        )
    
    def send_security_alert(
        self,
        user_email: str,
        user_name: str,
        security_data: Dict[str, Any]
    ) -> bool:
        """Send security alert notification"""
        return self.send_email(
            to_email=user_email,
            subject="Security Alert - CivicLogHOA Account",
            template_name="security_alert",
            template_data={
                "user_name": user_name,
                "event_type": security_data.get('event_type', ''),
                "location": security_data.get('location', ''),
                "device": security_data.get('device', ''),
                "timestamp": security_data.get('timestamp', ''),
                "ip_address": security_data.get('ip_address', '')
            }
        )

# Global email service instance
email_service = EmailAlertService()

def send_violation_notification_email(
    user_email: str,
    user_name: str,
    violation_data: Dict[str, Any]
) -> bool:
    """Send violation notification email"""
    return email_service.send_violation_notification(user_email, user_name, violation_data)

def send_violation_resolved_email(
    user_email: str,
    user_name: str,
    violation_data: Dict[str, Any]
) -> bool:
    """Send violation resolved email"""
    return email_service.send_violation_resolved_notification(user_email, user_name, violation_data)

def send_monthly_report_email(
    user_email: str,
    user_name: str,
    report_data: Dict[str, Any]
) -> bool:
    """Send monthly report email"""
    return email_service.send_monthly_report(user_email, user_name, report_data)

def send_security_alert_email(
    user_email: str,
    user_name: str,
    security_data: Dict[str, Any]
) -> bool:
    """Send security alert email"""
    return email_service.send_security_alert(user_email, user_name, security_data)
