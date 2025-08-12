# backend/utils/email_alerts.py
# Email alert system for ContractGuard.ai - AI Contract Review Platform

import os
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from utils.logger import get_logger

logger = get_logger("email_alerts")

# Email configuration
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
FROM_EMAIL = os.getenv("FROM_EMAIL", "noreply@contractguard.ai")
FROM_NAME = os.getenv("FROM_NAME", "ContractGuard.ai")

def send_email(
    to_email: str,
    subject: str,
    body: str,
    html_body: Optional[str] = None,
    attachments: Optional[List[Dict[str, Any]]] = None
) -> bool:
    """
    Send an email with optional HTML body and attachments.
    
    Args:
        to_email: Recipient email address
        subject: Email subject
        body: Plain text body
        html_body: Optional HTML body
        attachments: Optional list of attachment dictionaries with 'filename' and 'content' keys
        
    Returns:
        True if email sent successfully, False otherwise
    """
    try:
        if not SMTP_USERNAME or not SMTP_PASSWORD:
            logger.error("SMTP credentials not configured")
            return False
        
        # Create message
        msg = MIMEMultipart('alternative')
        msg['From'] = f"{FROM_NAME} <{FROM_EMAIL}>"
        msg['To'] = to_email
        msg['Subject'] = subject
        
        # Add plain text body
        text_part = MIMEText(body, 'plain')
        msg.attach(text_part)
        
        # Add HTML body if provided
        if html_body:
            html_part = MIMEText(html_body, 'html')
            msg.attach(html_part)
        
        # Add attachments if provided
        if attachments:
            for attachment in attachments:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment['content'])
                encoders.encode_base64(part)
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename= {attachment["filename"]}'
                )
                msg.attach(part)
        
        # Send email
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(msg)
        
        logger.info(f"Email sent successfully to {to_email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {e}")
        return False

def send_contract_analysis_notification(
    user_email: str,
    user_name: str,
    contract_title: str,
    analysis_status: str,
    risk_level: Optional[str] = None
) -> bool:
    """
    Send notification when contract analysis is completed.
    
    Args:
        user_email: User's email address
        user_name: User's name
        contract_title: Title of the analyzed contract
        analysis_status: Status of the analysis
        risk_level: Risk level if analysis completed
        
    Returns:
        True if email sent successfully, False otherwise
    """
    subject = f"Contract Analysis Complete: {contract_title}"
    
    if analysis_status == "completed":
        body = f"""
        Hello {user_name},
        
        Your contract analysis for "{contract_title}" has been completed successfully.
        
        Risk Level: {risk_level or 'Not specified'}
        
        You can view the full analysis results in your ContractGuard.ai dashboard.
        
        Best regards,
        The ContractGuard.ai Team
        """
        
        html_body = f"""
        <html>
        <body>
            <h2>Contract Analysis Complete</h2>
            <p>Hello {user_name},</p>
            <p>Your contract analysis for <strong>"{contract_title}"</strong> has been completed successfully.</p>
            <p><strong>Risk Level:</strong> {risk_level or 'Not specified'}</p>
            <p>You can view the full analysis results in your <a href="https://contractguard.ai/dashboard">ContractGuard.ai dashboard</a>.</p>
            <br>
            <p>Best regards,<br>The ContractGuard.ai Team</p>
        </body>
        </html>
        """
    else:
        body = f"""
        Hello {user_name},
        
        There was an issue with the analysis of your contract "{contract_title}".
        
        Status: {analysis_status}
        
        Please try uploading the contract again or contact support if the issue persists.
        
        Best regards,
        The ContractGuard.ai Team
        """
        
        html_body = f"""
        <html>
        <body>
            <h2>Contract Analysis Issue</h2>
            <p>Hello {user_name},</p>
            <p>There was an issue with the analysis of your contract <strong>"{contract_title}"</strong>.</p>
            <p><strong>Status:</strong> {analysis_status}</p>
            <p>Please try uploading the contract again or <a href="mailto:support@contractguard.ai">contact support</a> if the issue persists.</p>
            <br>
            <p>Best regards,<br>The ContractGuard.ai Team</p>
        </body>
        </html>
        """
    
    return send_email(user_email, subject, body, html_body)

def send_risk_alert_notification(
    user_email: str,
    user_name: str,
    contract_title: str,
    risk_items: List[Dict[str, Any]]
) -> bool:
    """
    Send notification for high-risk contracts.
    
    Args:
        user_email: User's email address
        user_name: User's name
        contract_title: Title of the contract
        risk_items: List of identified risks
        
    Returns:
        True if email sent successfully, False otherwise
    """
    subject = f"High Risk Alert: {contract_title}"
    
    # Count high and medium risks
    high_risks = [r for r in risk_items if r.get('severity', 0) >= 4]
    medium_risks = [r for r in risk_items if 2 <= r.get('severity', 0) < 4]
    
    body = f"""
    Hello {user_name},
    
    IMPORTANT: Your contract "{contract_title}" has been flagged with potential risks that require immediate attention.
    
    Risk Summary:
    - High Risk Items: {len(high_risks)}
    - Medium Risk Items: {len(medium_risks)}
    
    Please review the contract analysis in your dashboard and consider consulting with legal counsel before proceeding.
    
    Best regards,
    The ContractGuard.ai Team
    """
    
    html_body = f"""
    <html>
    <body>
        <h2 style="color: #dc2626;">🚨 High Risk Alert</h2>
        <p>Hello {user_name},</p>
        <p><strong>IMPORTANT:</strong> Your contract <strong>"{contract_title}"</strong> has been flagged with potential risks that require immediate attention.</p>
        
        <h3>Risk Summary:</h3>
        <ul>
            <li><strong style="color: #dc2626;">High Risk Items:</strong> {len(high_risks)}</li>
            <li><strong style="color: #f59e0b;">Medium Risk Items:</strong> {len(medium_risks)}</li>
        </ul>
        
        <p>Please review the contract analysis in your <a href="https://contractguard.ai/dashboard">dashboard</a> and consider consulting with legal counsel before proceeding.</p>
        
        <br>
        <p>Best regards,<br>The ContractGuard.ai Team</p>
    </body>
    </html>
    """
    
    return send_email(user_email, subject, body, html_body)

def send_workspace_invitation(
    user_email: str,
    user_name: str,
    workspace_name: str,
    inviter_name: str,
    invitation_link: str
) -> bool:
    """
    Send workspace invitation email.
    
    Args:
        user_email: User's email address
        user_name: User's name
        workspace_name: Name of the workspace
        inviter_name: Name of the person sending the invitation
        invitation_link: Link to accept the invitation
        
    Returns:
        True if email sent successfully, False otherwise
    """
    subject = f"You're invited to join {workspace_name} on ContractGuard.ai"
    
    body = f"""
    Hello {user_name},
    
    {inviter_name} has invited you to join the {workspace_name} workspace on ContractGuard.ai.
    
    ContractGuard.ai is an AI-powered contract review and risk management platform that helps teams:
    - Analyze contracts for potential risks
    - Generate comprehensive summaries
    - Track contract lifecycle and obligations
    - Ensure compliance and best practices
    
    To accept this invitation, please click the following link:
    {invitation_link}
    
    This invitation will expire in 7 days.
    
    If you have any questions, please contact {inviter_name} or our support team.
    
    Best regards,
    The ContractGuard.ai Team
    """
    
    html_body = f"""
    <html>
    <body>
        <h2>You're invited to join {workspace_name}</h2>
        <p>Hello {user_name},</p>
        <p><strong>{inviter_name}</strong> has invited you to join the <strong>{workspace_name}</strong> workspace on ContractGuard.ai.</p>
        
        <p>ContractGuard.ai is an AI-powered contract review and risk management platform that helps teams:</p>
        <ul>
            <li>Analyze contracts for potential risks</li>
            <li>Generate comprehensive summaries</li>
            <li>Track contract lifecycle and obligations</li>
            <li>Ensure compliance and best practices</li>
        </ul>
        
        <p>To accept this invitation, please click the following link:</p>
        <p><a href="{invitation_link}" style="background-color: #3b82f6; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; display: inline-block;">Accept Invitation</a></p>
        
        <p><em>This invitation will expire in 7 days.</em></p>
        
        <p>If you have any questions, please contact {inviter_name} or our <a href="mailto:support@contractguard.ai">support team</a>.</p>
        
        <br>
        <p>Best regards,<br>The ContractGuard.ai Team</p>
    </body>
    </html>
    """
    
    return send_email(user_email, subject, body, html_body)

def send_monthly_report(
    user_email: str,
    user_name: str,
    workspace_name: str,
    report_data: Dict[str, Any]
) -> bool:
    """
    Send monthly workspace report.
    
    Args:
        user_email: User's email address
        user_name: User's name
        workspace_name: Name of the workspace
        report_data: Monthly report data
        
    Returns:
        True if email sent successfully, False otherwise
    """
    subject = f"Monthly Report - {workspace_name} - {report_data.get('month_year', '')}"
    
    # Extract key metrics
    total_contracts = report_data.get('total_contracts', 0)
    analyzed_contracts = report_data.get('analyzed_contracts', 0)
    high_risk_contracts = report_data.get('high_risk_contracts', 0)
    
    body = f"""
    Hello {user_name},
    
    Here's your monthly report for {workspace_name}:
    
    Monthly Summary:
    - Total Contracts: {total_contracts}
    - Analyzed Contracts: {analyzed_contracts}
    - High Risk Contracts: {high_risk_contracts}
    
    You can view the complete report in your dashboard.
    
    Best regards,
    The ContractGuard.ai Team
    """
    
    html_body = f"""
    <html>
    <body>
        <h2>Monthly Report - {workspace_name}</h2>
        <p>Hello {user_name},</p>
        <p>Here's your monthly report for <strong>{workspace_name}</strong>:</p>
        
        <h3>Monthly Summary:</h3>
        <ul>
            <li><strong>Total Contracts:</strong> {total_contracts}</li>
            <li><strong>Analyzed Contracts:</strong> {analyzed_contracts}</li>
            <li><strong>High Risk Contracts:</strong> {high_risk_contracts}</li>
        </ul>
        
        <p>You can view the complete report in your <a href="https://contractguard.ai/dashboard">dashboard</a>.</p>
        
        <br>
        <p>Best regards,<br>The ContractGuard.ai Team</p>
    </body>
    </html>
    """
    
    return send_email(user_email, subject, body, html_body)

def send_system_notification(
    user_email: str,
    user_name: str,
    notification_type: str,
    message: str,
    action_required: bool = False
) -> bool:
    """
    Send system notification email.
    
    Args:
        user_email: User's email address
        user_name: User's name
        notification_type: Type of notification
        message: Notification message
        action_required: Whether action is required from the user
        
    Returns:
        True if email sent successfully, False otherwise
    """
    if action_required:
        subject = f"Action Required: {notification_type}"
    else:
        subject = f"System Notification: {notification_type}"
    
    body = f"""
    Hello {user_name},
    
    {message}
    
    {f'ACTION REQUIRED: Please review and take necessary action.' if action_required else 'This is an informational message only.'}
    
    Best regards,
    The ContractGuard.ai Team
    """
    
    html_body = f"""
    <html>
    <body>
        <h2>{'🚨 Action Required' if action_required else 'ℹ️ System Notification'}</h2>
        <p>Hello {user_name},</p>
        <p>{message}</p>
        
        {f'<p><strong style="color: #dc2626;">ACTION REQUIRED:</strong> Please review and take necessary action.</p>' if action_required else '<p><em>This is an informational message only.</em></p>'}
        
        <br>
        <p>Best regards,<br>The ContractGuard.ai Team</p>
    </body>
    </html>
    """
    
    return send_email(user_email, subject, body, html_body)
