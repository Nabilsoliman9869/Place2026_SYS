import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import threading

# Central Email Configuration
SMTP_SERVER = "smtp.gmail.com" # Or your corporate server
SMTP_PORT = 587
SMTP_USER = "place.guide.system@gmail.com" # Placeholder
SMTP_PASSWORD = "your_app_password" # Placeholder

def send_email_async(to_email, subject, body):
    """Sends an email in a separate thread to avoid blocking the UI."""
    if not to_email: return
    
    def _send():
        try:
            msg = MIMEMultipart()
            msg['From'] = SMTP_USER
            msg['To'] = to_email
            msg['Subject'] = f"[PGA System] {subject}"
            
            msg.attach(MIMEText(body, 'html'))
            
            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            server.starttls()
            # server.login(SMTP_USER, SMTP_PASSWORD) # Commented out until real creds provided
            # server.send_message(msg)
            server.quit()
            print(f">>> Email Simulation: Sent to {to_email} | Subject: {subject}")
        except Exception as e:
            print(f"!!! Email Error: {e}")

    # For now, we just print the simulation to console to avoid crashing without real creds
    print(f"\n[EMAIL SIMULATION] To: {to_email}\nSubject: {subject}\nBody: {body}\n")
    # threading.Thread(target=_send).start()

def notify_lead_assignment(agent_email, agent_name, lead_count, campaign_name):
    subject = "New Leads Assigned"
    body = f"""
    <h3>Hello {agent_name},</h3>
    <p>Marketing has assigned <b>{lead_count}</b> new leads to you from campaign <b>{campaign_name}</b>.</p>
    <p>Please check your dashboard to follow up.</p>
    <br>
    <small>Place Guide Academy System</small>
    """
    send_email_async(agent_email, subject, body)

def notify_slot_booking(ta_email, ta_name, candidate_name, date, time):
    subject = "New Assessment Booked"
    body = f"""
    <h3>Hello {ta_name},</h3>
    <p>Sales has booked a new assessment for candidate <b>{candidate_name}</b>.</p>
    <ul>
        <li>Date: {date}</li>
        <li>Time: {time}</li>
    </ul>
    <p>Please be ready.</p>
    """
    send_email_async(ta_email, subject, body)

def notify_no_show(sales_email, sales_name, candidate_name, reason):
    subject = "Urgent: Candidate No-Show"
    body = f"""
    <h3>Hello {sales_name},</h3>
    <p>Your candidate <b>{candidate_name}</b> did not attend the scheduled assessment.</p>
    <p><b>Reason:</b> {reason}</p>
    <p>Please contact them immediately to reschedule.</p>
    """
    send_email_async(sales_email, subject, body)
