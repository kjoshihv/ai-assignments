import asyncio
import re
import requests  # Import requests for Telegram API
import logging  # Import logging
import smtplib  # Import smtplib for sending emails
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Configure logging
logging.basicConfig(
    filename="application.log",
    level=logging.INFO,
    format="%(filename)s %(funcName)s %(asctime)s - %(levelname)s - %(message)s"
)

async def generate_with_timeout(client, prompt, timeout=20):
    """Generate content with a timeout."""
    try:
        loop = asyncio.get_event_loop()
        response = await asyncio.wait_for(
            loop.run_in_executor(
                None,
                lambda: client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=prompt
                )
            ),
            timeout=timeout
        )
        return response
    except Exception as e:
        logging.error(f"Error: {e}")
        return None

def remove_markdown(response):
    """Remove code block markers from the response."""
    cleaned_response = re.sub(r'```(?:json|python|.*)?\n', '', response)
    cleaned_response = re.sub(r'\n```', '', cleaned_response)
    return cleaned_response

def send_email_via_gmail(sender_email, sender_password, recipient_email, subject, body):
    """Send an email via Gmail."""
    try:
        # Set up the MIME message
        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = recipient_email
        message["Subject"] = subject
        message.attach(MIMEText(body, "plain"))

        # Connect to Gmail's SMTP server
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()  # Upgrade the connection to secure
            server.login(sender_email, sender_password)  # Log in to the sender's email account
            server.sendmail(sender_email, recipient_email, message.as_string())  # Send the email

        logging.info(f"Email sent successfully to {recipient_email}.")
    except Exception as e:
        logging.error(f"Error sending email: {e}")

