# utils/email_service.py
"""
Email service for ContractGuard - AI Contract Review Platform
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
from models import ContractRecord, User, Workspace

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
    
    def send_contract_notification(
        self, 
        contract: ContractRecord, 
        recipient_email: str,
        notification_type: str = "initial"
    ) -> bool:
        """Send contract notification email."""
        try:
            subject = f"Contract Notification - {contract.title}"
            
            html_body = self._create_contract_notification_html(contract, notification_type)
            text_body = self._create_contract_notification_text(contract, notification_type)
            
            return self.send_email(recipient_email, subject, text_body, html_body)
            
        except Exception as e:
            logger.error(f"Failed to send contract notification: {e}")
            return False

    def send_contract_escalation_notification(
        self, 
        contract: ContractRecord, 
        recipient_email: str,
        escalation_reason: str
    ) -> bool:
        """Send contract escalation notification email."""
        try:
            subject = f"Contract Escalation - {contract.title}"
            
            html_body = f"""
            <h2>Contract Escalation Required</h2>
            <p>The contract <strong>{contract.title}</strong> has been escalated for review.</p>
            <p><strong>Reason:</strong> {escalation_reason}</p>
            <p><strong>Contract Details:</strong></p>
            <ul>
                <li>Title: {contract.title}</li>
                <li>Counterparty: {contract.counterparty}</li>
                <li>Category: {contract.category}</li>
                <li>Status: {contract.status}</li>
            </ul>
            <p>Please review this contract as soon as possible.</p>
            <p>Best regards,<br>ContractGuard.ai Team</p>
            """
            
            text_body = f"""
            Contract Escalation Required
            
            The contract {contract.title} has been escalated for review.
            
            Reason: {escalation_reason}
            
            Contract Details:
            - Title: {contract.title}
            - Counterparty: {contract.counterparty}
            - Category: {contract.category}
            - Status: {contract.status}
            
            Please review this contract as soon as possible.
            
            Best regards,
            ContractGuard.ai Team
            """
            
            return self.send_email(recipient_email, subject, text_body, html_body)
            
        except Exception as e:
            logger.error(f"Failed to send contract escalation notification: {e}")
            return False

    def send_contract_review_notification(
        self, 
        contract: ContractRecord, 
        recipient_email: str,
        reviewer: User
    ) -> bool:
        """Send contract review notification email."""
        try:
            subject = f"Contract Review Required - {contract.title}"
            
            html_body = f"""
            <h2>Contract Review Required</h2>
            <p>The contract <strong>{contract.title}</strong> has been assigned to you for review.</p>
            <p><strong>Contract Details:</strong></p>
            <ul>
                <li>Title: {contract.title}</li>
                <li>Counterparty: {contract.counterparty}</li>
                <li>Category: {contract.category}</li>
                <li>Status: {contract.status}</li>
            </ul>
            <p>Please review this contract and provide your analysis.</p>
            <p>Best regards,<br>ContractGuard.ai Team</p>
            """
            
            text_body = f"""
            Contract Review Required
            
            The contract {contract.title} has been assigned to you for review.
            
            Contract Details:
            - Title: {contract.title}
            - Counterparty: {contract.counterparty}
            - Category: {contract.category}
            - Status: {contract.status}
            
            Please review this contract and provide your analysis.
            
            Best regards,
            ContractGuard.ai Team
            """
            
            return self.send_email(recipient_email, subject, text_body, html_body)
            
        except Exception as e:
            logger.error(f"Failed to send contract review notification: {e}")
            return False

    def send_contract_approval_notification(
        self, 
        contract: ContractRecord, 
        recipient_email: str,
        approved_by: str,
        approval_notes: Optional[str] = None
    ) -> bool:
        """Send contract approval notification email."""
        try:
            subject = f"Contract Approved - {contract.title}"
            
            notes_html = f"<p><strong>Approval Notes:</strong> {approval_notes}</p>" if approval_notes else ""
            notes_text = f"\nApproval Notes: {approval_notes}" if approval_notes else ""
            
            html_body = f"""
            <h2>Contract Approved</h2>
            <p>The contract <strong>{contract.title}</strong> has been approved by {approved_by}.</p>
            <p><strong>Contract Details:</strong></p>
            <ul>
                <li>Title: {contract.title}</li>
                <li>Counterparty: {contract.counterparty}</li>
                <li>Category: {contract.category}</li>
                <li>Status: {contract.status}</li>
            </ul>
            {notes_html}
            <p>Best regards,<br>ContractGuard.ai Team</p>
            """
            
            text_body = f"""
            Contract Approved
            
            The contract {contract.title} has been approved by {approved_by}.
            
            Contract Details:
            - Title: {contract.title}
            - Counterparty: {contract.counterparty}
            - Category: {contract.category}
            - Status: {contract.status}
            {notes_text}
            
            Best regards,
            ContractGuard.ai Team
            """
            
            return self.send_email(recipient_email, subject, text_body, html_body)
            
        except Exception as e:
            logger.error(f"Failed to send contract approval notification: {e}")
            return False

    def send_contract_rejection_notification(
        self, 
        contract: ContractRecord, 
        recipient_email: str,
        rejected_by: str,
        rejection_reason: str
    ) -> bool:
        """Send contract rejection notification email."""
        try:
            subject = f"Contract Rejected - {contract.title}"
            
            html_body = f"""
            <h2>Contract Rejected</h2>
            <p>The contract <strong>{contract.title}</strong> has been rejected by {rejected_by}.</p>
            <p><strong>Rejection Reason:</strong> {rejection_reason}</p>
            <p><strong>Contract Details:</strong></p>
            <ul>
                <li>Title: {contract.title}</li>
                <li>Counterparty: {contract.counterparty}</li>
                <li>Category: {contract.category}</li>
                <li>Status: {contract.status}</li>
            </ul>
            <p>Please review the rejection reason and make necessary changes.</p>
            <p>Best regards,<br>ContractGuard.ai Team</p>
            """
            
            text_body = f"""
            Contract Rejected
            
            The contract {contract.title} has been rejected by {rejected_by}.
            
            Rejection Reason: {rejection_reason}
            
            Contract Details:
            - Title: {contract.title}
            - Counterparty: {contract.counterparty}
            - Category: {contract.category}
            - Status: {contract.status}
            
            Please review the rejection reason and make necessary changes.
            
            Best regards,
            ContractGuard.ai Team
            """
            
            return self.send_email(recipient_email, subject, text_body, html_body)
            
        except Exception as e:
            logger.error(f"Failed to send contract rejection notification: {e}")
            return False

    def send_contract_analysis_complete_notification(
        self, 
        contract: ContractRecord, 
        recipient_email: str
    ) -> bool:
        """Send contract analysis complete notification email."""
        try:
            subject = f"Contract Analysis Complete - {contract.title}"
            
            html_body = f"""
            <h2>Contract Analysis Complete</h2>
            <p>The AI analysis for contract <strong>{contract.title}</strong> has been completed.</p>
            <p><strong>Contract Details:</strong></p>
            <ul>
                <li>Title: {contract.title}</li>
                <li>Counterparty: {contract.counterparty}</li>
                <li>Category: {contract.category}</li>
                <li>Status: {contract.status}</li>
            </ul>
            <p>Please review the analysis results and take appropriate action.</p>
            <p>Best regards,<br>ContractGuard.ai Team</p>
            """
            
            text_body = f"""
            Contract Analysis Complete
            
            The AI analysis for contract {contract.title} has been completed.
            
            Contract Details:
            - Title: {contract.title}
            - Counterparty: {contract.counterparty}
            - Category: {contract.category}
            - Status: {contract.status}
            
            Please review the analysis results and take appropriate action.
            
            Best regards,
            ContractGuard.ai Team
            """
            
            return self.send_email(recipient_email, subject, text_body, html_body)
            
        except Exception as e:
            logger.error(f"Failed to send contract analysis complete notification: {e}")
            return False

    def send_contract_risk_alert(
        self, 
        contract: ContractRecord, 
        recipient_email: str,
        risk_level: str,
        risk_details: str
    ) -> bool:
        """Send contract risk alert email."""
        try:
            subject = f"Risk Alert - {contract.title}"
            
            risk_color = "#ff4444" if risk_level.lower() == "high" else "#ff8800" if risk_level.lower() == "medium" else "#00aa00"
            
            html_body = f"""
            <h2>Contract Risk Alert</h2>
            <p>A <span style="color: {risk_color}; font-weight: bold;">{risk_level.upper()}</span> risk has been identified in contract <strong>{contract.title}</strong>.</p>
            <p><strong>Risk Details:</strong></p>
            <div style="background-color: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; margin: 15px 0; border-radius: 5px;">
                {risk_details}
            </div>
            <p><strong>Contract Details:</strong></p>
            <ul>
                <li>Title: {contract.title}</li>
                <li>Counterparty: {contract.counterparty}</li>
                <li>Category: {contract.category}</li>
                <li>Status: {contract.status}</li>
            </ul>
            <p>Please review this contract immediately and take appropriate action.</p>
            <p>Best regards,<br>ContractGuard.ai Team</p>
            """
            
            text_body = f"""
            Contract Risk Alert
            
            A {risk_level.upper()} risk has been identified in contract {contract.title}.
            
            Risk Details:
            {risk_details}
            
            Contract Details:
            - Title: {contract.title}
            - Counterparty: {contract.counterparty}
            - Category: {contract.category}
            - Status: {contract.status}
            
            Please review this contract immediately and take appropriate action.
            
            Best regards,
            ContractGuard.ai Team
            """
            
            return self.send_email(recipient_email, subject, text_body, html_body)
            
        except Exception as e:
            logger.error(f"Failed to send contract risk alert: {e}")
            return False

    def _create_contract_notification_html(self, contract: ContractRecord, notification_type: str) -> str:
        """Create HTML body for contract notification."""
        return f"""
        <html>
        <body>
            <h2>Contract Notification</h2>
            <p>A new contract has been uploaded and requires attention:</p>
            
            <div style="background-color: #f8f9fa; border: 1px solid #dee2e6; padding: 15px; margin: 15px 0; border-radius: 5px;">
                <h3>Contract Details:</h3>
                <p><strong>Title:</strong> {contract.title}</p>
                <p><strong>Counterparty:</strong> {contract.counterparty}</p>
                <p><strong>Category:</strong> {contract.category}</p>
                <p><strong>Status:</strong> {contract.status}</p>
                <p><strong>Uploaded:</strong> {contract.created_at.strftime('%Y-%m-%d %H:%M:%S') if contract.created_at else 'N/A'}</p>
            </div>
            
            <p>Please review this contract and take appropriate action.</p>
            
            <p>Best regards,<br>ContractGuard.ai Team</p>
        </body>
        </html>
        """

    def _create_contract_notification_text(self, contract: ContractRecord, notification_type: str) -> str:
        """Create text body for contract notification."""
        return f"""
        Contract Notification
        
        A new contract has been uploaded and requires attention:
        
        Contract Details:
        - Title: {contract.title}
        - Counterparty: {contract.counterparty}
        - Category: {contract.category}
        - Status: {contract.status}
        - Uploaded: {contract.created_at.strftime('%Y-%m-%d %H:%M:%S') if contract.created_at else 'N/A'}
        
        Please review this contract and take appropriate action.
        
        Best regards,
        ContractGuard.ai Team
        """


# Global email service instance
email_service = EmailService()

def send_email(
    to_email: str,
    subject: str,
    html_content: str,
    text_content: str = ""
) -> bool:
    """Standalone function to send email for resident invitations."""
    return email_service.send_email(
        to_email=to_email,
        subject=subject,
        body=text_content,
        html_body=html_content
    ) 