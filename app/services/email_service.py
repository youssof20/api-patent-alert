"""
Email notification service
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
import logging
from app.config import settings

logger = logging.getLogger(__name__)

# Fix contact email reference
CONTACT_EMAIL = "betterappsstudio@gmail.com"


class EmailService:
    """Service for sending email notifications"""
    
    def __init__(self):
        self.smtp_server = getattr(settings, 'smtp_server', 'smtp.gmail.com')
        self.smtp_port = getattr(settings, 'smtp_port', 587)
        self.smtp_user = getattr(settings, 'smtp_user', '')
        self.smtp_password = getattr(settings, 'smtp_password', '')
        self.from_email = getattr(settings, 'from_email', settings.smtp_user or 'noreply@patentalert.com')
        self.enabled = bool(self.smtp_user and self.smtp_password)
    
    def _send_email(
        self,
        to_email: str,
        subject: str,
        body_html: str,
        body_text: Optional[str] = None
    ) -> bool:
        """Send email via SMTP"""
        if not self.enabled:
            logger.warning(f"Email not configured. Would send to {to_email}: {subject}")
            return False
        
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.from_email
            msg['To'] = to_email
            
            # Add both plain text and HTML versions
            if body_text:
                part1 = MIMEText(body_text, 'plain')
                msg.attach(part1)
            
            part2 = MIMEText(body_html, 'html')
            msg.attach(part2)
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
            
            logger.info(f"Email sent to {to_email}: {subject}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}")
            return False
    
    def send_welcome_email(self, partner_email: str, partner_name: str, api_key: str):
        """Send welcome email when API key is created"""
        subject = "Welcome to Patent Alert API - Your API Key"
        
        body_html = f"""
        <html>
        <body>
            <h2>Welcome to Patent Alert API, {partner_name}!</h2>
            <p>Your API key has been created successfully.</p>
            <p><strong>API Key:</strong> <code>{api_key}</code></p>
            <p><strong>Important:</strong> Save this key securely - it won't be shown again.</p>
            <h3>Quick Start:</h3>
            <ol>
                <li>Visit <a href="https://api-patent-alert.onrender.com/docs">API Documentation</a></li>
                <li>Click the "Authorize" button (🔒) in the top right</li>
                <li>Enter your API key and start testing</li>
            </ol>
            <h3>Free Trial:</h3>
            <ul>
                <li>14 days free trial (no credit card required)</li>
                <li>Full feature access</li>
                <li>Pricing: Starter $499/mo | Professional $1,999/mo</li>
            </ul>
            <p>Need help? Contact us at {CONTACT_EMAIL}</p>
            <p>Best regards,<br>Patent Alert API Team</p>
        </body>
        </html>
        """
        
        body_text = f"""
        Welcome to Patent Alert API, {partner_name}!
        
        Your API key: {api_key}
        
        Important: Save this key securely - it won't be shown again.
        
        Quick Start:
        1. Visit https://api-patent-alert.onrender.com/docs
        2. Click the "Authorize" button
        3. Enter your API key and start testing
        
        Free Trial: 14 days (no credit card required)
        Pricing: Starter $499/mo | Professional $1,999/mo
        
        Need help? Contact us at {CONTACT_EMAIL}
        """
        
        return self._send_email(partner_email, subject, body_html, body_text)
    
    def send_usage_alert(self, partner_email: str, partner_name: str, usage_percent: float):
        """Send alert when approaching rate limit"""
        subject = f"Patent Alert API - Usage Alert ({usage_percent:.0f}% of limit)"
        
        body_html = f"""
        <html>
        <body>
            <h2>Usage Alert - {partner_name}</h2>
            <p>You've used <strong>{usage_percent:.0f}%</strong> of your daily rate limit.</p>
            <p>Consider upgrading your plan to avoid hitting limits.</p>
            <p><a href="http://localhost:8000/docs">View Usage Stats</a></p>
        </body>
        </html>
        """
        
        return self._send_email(partner_email, subject, body_html)
    
    def send_trial_ending_email(self, partner_email: str, partner_name: str, days_left: int):
        """Send email when trial is ending"""
        subject = f"Patent Alert API - Trial Ending in {days_left} Days"
        
        body_html = f"""
        <html>
        <body>
            <h2>Trial Ending Soon - {partner_name}</h2>
            <p>Your free trial ends in <strong>{days_left} days</strong>.</p>
            <p>Upgrade now to continue using the API without interruption.</p>
            <p><a href="http://localhost:8000/docs">Upgrade Plan</a></p>
        </body>
        </html>
        """
        
        return self._send_email(partner_email, subject, body_html)

