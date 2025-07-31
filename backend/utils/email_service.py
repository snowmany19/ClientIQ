# utils/email_service.py
"""
Email service for CivicLogHOA - HOA Violation Management Platform
Handles all email notifications, warnings, and communications
"""

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import List, Optional, Dict, Any
from datetime import datetime
import os
from pathlib import Path

from core.config import get_settings
from utils.logger import get_logger
from models import Violation, User, Resident, Dispute

logger = get_logger("email_service")
settings = get_settings()


class EmailService:
    """Email service for sending notifications and communications."""
    
    def __init__(self):
        self.smtp_server = settings.smtp_server
        self.smtp_port = settings.smtp_port
        self.smtp_username = settings.smtp_username
        self.smtp_password = settings.smtp_password
        self.from_email = settings.smtp_username
        
    def _create_smtp_connection(self) -> Optional[smtplib.SMTP]:
        """Create SMTP connection with proper error handling."""
        try:
            if not self.smtp_username or not self.smtp_password:
                logger.warning("SMTP credentials not configured, skipping email send")
                return None
                
            context = ssl.create_default_context()
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls(context=context)
            server.login(self.smtp_username, self.smtp_password)
            return server
            
        except Exception as e:
            logger.error(f"Failed to create SMTP connection: {e}")
            return None
    
    def send_email(
        self, 
        to_email: str, 
        subject: str, 
        body: str, 
        html_body: Optional[str] = None,
        attachments: Optional[List[Dict[str, Any]]] = None
    ) -> bool:
        """Send email with optional HTML and attachments."""
        try:
            server = self._create_smtp_connection()
            if not server:
                return False
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = self.from_email
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Add text body
            text_part = MIMEText(body, 'plain')
            msg.attach(text_part)
            
            # Add HTML body if provided
            if html_body:
                html_part = MIMEText(html_body, 'html')
                msg.attach(html_part)
            
            # Add attachments if provided
            if attachments:
                for attachment in attachments:
                    self._add_attachment(msg, attachment)
            
            # Send email
            server.send_message(msg)
            server.quit()
            
            logger.info(f"Email sent successfully to {to_email}: {subject}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}")
            return False
    
    def _add_attachment(self, msg: MIMEMultipart, attachment: Dict[str, Any]) -> None:
        """Add attachment to email message."""
        try:
            file_path = attachment.get('file_path')
            filename = attachment.get('filename', os.path.basename(file_path))
            content_type = attachment.get('content_type', 'application/octet-stream')
            
            if not file_path or not os.path.exists(file_path):
                logger.warning(f"Attachment file not found: {file_path}")
                return
            
            with open(file_path, "rb") as file:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(file.read())
            
            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename= {filename}'
            )
            msg.attach(part)
            
        except Exception as e:
            logger.error(f"Failed to add attachment: {e}")
    
    def send_violation_notification(
        self, 
        violation: Violation, 
        recipient_email: str,
        notification_type: str = "initial"
    ) -> bool:
        """Send violation notification email."""
        try:
            subject = f"{notification_type.title()} Violation Notice - {violation.hoa_name}"
            
            # Create HTML body
            html_body = self._create_violation_notification_html(violation, notification_type)
            
            # Create text body
            text_body = self._create_violation_notification_text(violation, notification_type)
            
            return self.send_email(recipient_email, subject, text_body, html_body)
            
        except Exception as e:
            logger.error(f"Failed to send violation notification: {e}")
            return False
    
    def send_escalation_notification(
        self, 
        violation: Violation, 
        recipient_email: str,
        escalation_reason: str
    ) -> bool:
        """Send escalation notification email."""
        try:
            subject = f"URGENT: Violation Escalation - {violation.hoa_name}"
            
            html_body = f"""
            <html>
            <body>
                <h2>🚨 Violation Escalation Notice</h2>
                <p>A violation has been escalated for immediate HOA board review:</p>
                
                <div style="background-color: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; margin: 15px 0; border-radius: 5px;">
                    <h3>Violation Details:</h3>
                    <p><strong>Violation #:</strong> {violation.violation_number}</p>
                    <p><strong>Address:</strong> {violation.address}</p>
                    <p><strong>Resident:</strong> {violation.offender}</p>
                    <p><strong>Repeat Offender Score:</strong> {violation.repeat_offender_score}</p>
                    <p><strong>Status:</strong> {violation.status}</p>
                    <p><strong>Escalation Reason:</strong> {escalation_reason}</p>
                </div>
                
                <p>This violation requires immediate attention from the HOA board.</p>
                
                <p>Best regards,<br>CivicLogHOA Team</p>
            </body>
            </html>
            """
            
            text_body = f"""
            URGENT: Violation Escalation - {violation.hoa_name}
            
            A violation has been escalated for immediate HOA board review:
            
            Violation #: {violation.violation_number}
            Address: {violation.address}
            Resident: {violation.offender}
            Repeat Offender Score: {violation.repeat_offender_score}
            Status: {violation.status}
            Escalation Reason: {escalation_reason}
            
            This violation requires immediate attention from the HOA board.
            
            Best regards,
            CivicLogHOA Team
            """
            
            return self.send_email(recipient_email, subject, text_body, html_body)
            
        except Exception as e:
            logger.error(f"Failed to send escalation notification: {e}")
            return False
    
    def send_dispute_notification(
        self, 
        dispute: Dispute, 
        violation: Violation, 
        resident: Resident,
        recipient_email: str
    ) -> bool:
        """Send dispute notification email."""
        try:
            subject = f"New Dispute Filed - Violation #{violation.violation_number}"
            
            html_body = f"""
            <html>
            <body>
                <h2>📋 New Dispute Filed</h2>
                <p>A new dispute has been filed for review:</p>
                
                <div style="background-color: #e3f2fd; border: 1px solid #bbdefb; padding: 15px; margin: 15px 0; border-radius: 5px;">
                    <h3>Dispute Details:</h3>
                    <p><strong>Violation #:</strong> {violation.violation_number}</p>
                    <p><strong>Resident:</strong> {resident.name}</p>
                    <p><strong>Address:</strong> {resident.address}</p>
                    <p><strong>Reason:</strong> {dispute.reason}</p>
                    <p><strong>Contact Preference:</strong> {dispute.contact_preference}</p>
                    <p><strong>Submitted:</strong> {dispute.submitted_at.strftime('%Y-%m-%d %H:%M')}</p>
                </div>
                
                <p>Please review and respond accordingly.</p>
                
                <p>Best regards,<br>CivicLogHOA Team</p>
            </body>
            </html>
            """
            
            text_body = f"""
            New Dispute Filed - Violation #{violation.violation_number}
            
            A new dispute has been filed:
            
            Violation #: {violation.violation_number}
            Resident: {resident.name}
            Address: {resident.address}
            Reason: {dispute.reason}
            Contact Preference: {dispute.contact_preference}
            Submitted: {dispute.submitted_at.strftime('%Y-%m-%d %H:%M')}
            
            Please review and respond accordingly.
            
            Best regards,
            CivicLogHOA Team
            """
            
            return self.send_email(recipient_email, subject, text_body, html_body)
            
        except Exception as e:
            logger.error(f"Failed to send dispute notification: {e}")
            return False
    
    def send_resolution_notification(
        self, 
        violation: Violation, 
        recipient_email: str,
        resolved_by: str,
        resolution_notes: Optional[str] = None
    ) -> bool:
        """Send resolution notification email."""
        try:
            subject = f"Violation #{violation.violation_number} Resolved - {violation.hoa_name}"
            
            html_body = f"""
            <html>
            <body>
                <h2>✅ Violation Resolved</h2>
                <p>The following violation has been marked as resolved:</p>
                
                <div style="background-color: #d4edda; border: 1px solid #c3e6cb; padding: 15px; margin: 15px 0; border-radius: 5px;">
                    <h3>Resolution Details:</h3>
                    <p><strong>Violation #:</strong> {violation.violation_number}</p>
                    <p><strong>Address:</strong> {violation.address}</p>
                    <p><strong>Resident:</strong> {violation.offender}</p>
                    <p><strong>Resolved by:</strong> {resolved_by}</p>
                    <p><strong>Resolved at:</strong> {violation.resolved_at.strftime('%Y-%m-%d %H:%M') if violation.resolved_at else 'N/A'}</p>
                    {f'<p><strong>Resolution notes:</strong> {resolution_notes}</p>' if resolution_notes else ''}
                </div>
                
                <p>This violation is now closed and archived.</p>
                
                <p>Best regards,<br>CivicLogHOA Team</p>
            </body>
            </html>
            """
            
            text_body = f"""
            Violation #{violation.violation_number} Resolved - {violation.hoa_name}
            
            The following violation has been marked as resolved:
            
            Violation #: {violation.violation_number}
            Address: {violation.address}
            Resident: {violation.offender}
            Resolved by: {resolved_by}
            Resolved at: {violation.resolved_at.strftime('%Y-%m-%d %H:%M') if violation.resolved_at else 'N/A'}
            {f'Resolution notes: {resolution_notes}' if resolution_notes else ''}
            
            This violation is now closed and archived.
            
            Best regards,
            CivicLogHOA Team
            """
            
            return self.send_email(recipient_email, subject, text_body, html_body)
            
        except Exception as e:
            logger.error(f"Failed to send resolution notification: {e}")
            return False
    
    def send_formal_warning(
        self, 
        violation: Violation, 
        recipient_email: str,
        pdf_path: Optional[str] = None
    ) -> bool:
        """Send formal warning email with optional PDF attachment."""
        try:
            subject = f"Formal Warning - Violation #{violation.violation_number} - {violation.hoa_name}"
            
            html_body = f"""
            <html>
            <body>
                <h2>⚠️ Formal Warning Notice</h2>
                <p>A formal warning has been issued for the following violation:</p>
                
                <div style="background-color: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; margin: 15px 0; border-radius: 5px;">
                    <h3>Violation Details:</h3>
                    <p><strong>Violation #:</strong> {violation.violation_number}</p>
                    <p><strong>Address:</strong> {violation.address}</p>
                    <p><strong>Resident:</strong> {violation.offender}</p>
                    <p><strong>Description:</strong> {violation.description}</p>
                    <p><strong>Repeat Offender Score:</strong> {violation.repeat_offender_score}</p>
                </div>
                
                <p>Please review the attached PDF for details and required corrective actions.</p>
                <p><strong>This is a formal warning and may result in fines if not addressed promptly.</strong></p>
                
                <p>Best regards,<br>CivicLogHOA Team</p>
            </body>
            </html>
            """
            
            text_body = f"""
            Formal Warning - Violation #{violation.violation_number} - {violation.hoa_name}
            
            A formal warning has been issued for the following violation:
            
            Violation #: {violation.violation_number}
            Address: {violation.address}
            Resident: {violation.offender}
            Description: {violation.description}
            Repeat Offender Score: {violation.repeat_offender_score}
            
            Please review the attached PDF for details and required corrective actions.
            
            This is a formal warning and may result in fines if not addressed promptly.
            
            Best regards,
            CivicLogHOA Team
            """
            
            attachments = []
            if pdf_path and os.path.exists(pdf_path):
                attachments.append({
                    'file_path': pdf_path,
                    'filename': f"violation_{violation.violation_number}_warning.pdf",
                    'content_type': 'application/pdf'
                })
            
            return self.send_email(recipient_email, subject, text_body, html_body, attachments)
            
        except Exception as e:
            logger.error(f"Failed to send formal warning: {e}")
            return False
    
    def send_violation_letter(
        self, 
        violation, 
        recipient_email: str,
        letter_content: str,
        pdf_path: Optional[str] = None,
        sent_by_user_id: Optional[int] = None
    ) -> bool:
        """Send violation letter email with optional PDF attachment."""
        try:
            subject = f"Official HOA Violation Notice - #{violation.violation_number} - {violation.hoa_name}"
            
            # Create HTML body for the letter
            html_body = f"""
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: #3b82f6; color: white; padding: 20px; text-align: center; }}
                    .content {{ padding: 20px; background: #f9fafb; }}
                    .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
                    .letter-content {{ background: white; padding: 20px; margin: 15px 0; border-left: 4px solid #3b82f6; white-space: pre-line; }}
                    .button {{ display: inline-block; padding: 10px 20px; background: #3b82f6; color: white; text-decoration: none; border-radius: 5px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>📋 Official HOA Violation Notice</h1>
                        <p>Violation #{violation.violation_number}</p>
                    </div>
                    <div class="content">
                        <p>Dear Resident,</p>
                        <p>This is an official notice regarding a violation of the HOA community guidelines.</p>
                        
                        <div class="letter-content">
                            {letter_content}
                        </div>
                        
                        <p>You can also view this violation and submit any disputes through your resident portal.</p>
                        
                        <a href="{os.getenv('APP_URL', 'http://localhost:3000')}/dashboard/resident-portal" class="button">
                            View in Resident Portal
                        </a>
                    </div>
                    <div class="footer">
                        <p>This is an official communication from {violation.hoa_name}</p>
                        <p>© {datetime.now().year} CivicLogHOA. All rights reserved.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            # Create text body
            text_body = f"""
            Official HOA Violation Notice - #{violation.violation_number} - {violation.hoa_name}
            
            Dear Resident,
            
            This is an official notice regarding a violation of the HOA community guidelines.
            
            {letter_content}
            
            You can also view this violation and submit any disputes through your resident portal.
            
            Best regards,
            {violation.hoa_name} Management Team
            """
            
            # Prepare attachments
            attachments = []
            if pdf_path and os.path.exists(pdf_path):
                attachments.append({
                    'file_path': pdf_path,
                    'filename': f"violation_letter_{violation.violation_number}_{datetime.now().strftime('%Y%m%d')}.pdf",
                    'content_type': 'application/pdf'
                })
            
            # Send email
            success = self.send_email(recipient_email, subject, text_body, html_body, attachments)
            
            if success:
                logger.info(f"Violation letter sent successfully to {recipient_email} for violation {violation.id}")
            else:
                logger.error(f"Failed to send violation letter to {recipient_email} for violation {violation.id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to send violation letter: {e}")
            return False
    
    def _create_violation_notification_html(self, violation: Violation, notification_type: str) -> str:
        """Create HTML body for violation notification."""
        severity_color = "#ff4444" if violation.repeat_offender_score > 2 else "#ff8800" if violation.repeat_offender_score > 1 else "#00aa00"
        severity_text = "High" if violation.repeat_offender_score > 2 else "Medium" if violation.repeat_offender_score > 1 else "Low"
        
        return f"""
        <html>
        <body>
            <h2>📋 {notification_type.title()} Violation Notice</h2>
            <p>A new violation has been reported in your HOA:</p>
            
            <div style="background-color: #f8f9fa; border: 1px solid #dee2e6; padding: 15px; margin: 15px 0; border-radius: 5px;">
                <h3>Violation Details:</h3>
                <p><strong>Violation #:</strong> {violation.violation_number}</p>
                <p><strong>Address:</strong> {violation.address}</p>
                <p><strong>Location:</strong> {violation.location}</p>
                <p><strong>Resident:</strong> {violation.offender}</p>
                <p><strong>Description:</strong> {violation.description}</p>
                <p><strong>Severity:</strong> <span style="color: {severity_color};">{severity_text}</span></p>
                <p><strong>Repeat Offender Score:</strong> {violation.repeat_offender_score}</p>
                <p><strong>Reported:</strong> {violation.timestamp.strftime('%Y-%m-%d %H:%M')}</p>
            </div>
            
            <p>Please review and take appropriate action.</p>
            
            <p>Best regards,<br>CivicLogHOA Team</p>
        </body>
        </html>
        """
    
    def _create_violation_notification_text(self, violation: Violation, notification_type: str) -> str:
        """Create text body for violation notification."""
        return f"""
        {notification_type.title()} Violation Notice - {violation.hoa_name}
        
        A new violation has been reported:
        
        Violation #: {violation.violation_number}
        Address: {violation.address}
        Location: {violation.location}
        Resident: {violation.offender}
        Description: {violation.description}
        Repeat Offender Score: {violation.repeat_offender_score}
        Reported: {violation.timestamp.strftime('%Y-%m-%d %H:%M')}
        
        Please review and take appropriate action.
        
        Best regards,
        CivicLogHOA Team
        """


# Global email service instance
email_service = EmailService() 