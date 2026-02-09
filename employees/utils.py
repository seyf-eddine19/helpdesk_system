from django.conf import settings
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

# ---------------- SENDGRID ----------------
def send_email_via_sendgrid(to, subject, content):
    message = Mail(
        from_email=settings.SENDGRID_FROM_EMAIL,
        to_emails=to,
        subject=subject,
        html_content=content,
    )

    sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
    response = sg.send(message)

    return {
        "status_code": response.status_code,
    }
