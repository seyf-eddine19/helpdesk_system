import requests
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from django.conf import settings

def get_access_token():
    """تجديد Access Token باستخدام Refresh Token"""
    url = "https://accounts.zoho.com/oauth/v2/token"
    data = {
        "refresh_token": settings.ZOHO_REFRESH_TOKEN,
        "client_id": settings.ZOHO_CLIENT_ID,
        "client_secret": settings.ZOHO_CLIENT_SECRET,
        "grant_type": "refresh_token"
    }
    res = requests.post(url, data=data)
    res.raise_for_status()
    return res.json().get("access_token")

def send_email(to, subject, content):
    """إرسال البريد عبر Zoho API"""
    access_token = get_access_token()
    url = f"https://mail.zoho.com/api/accounts/{settings.ZOHO_ACCOUNT_ID}/messages"
    headers = {
        "Authorization": f"Zoho-oauthtoken {access_token}",
        "Content-Type": "application/json"
    }
    data = {
        "fromAddress": settings.ZOHO_FROM_EMAIL,
        "toAddress": to,
        "subject": subject,
        "content": content
    }
    res = requests.post(url, headers=headers, json=data)
    res.raise_for_status()
    return res.json()

def send_email_via_api(to, subject, content):
    access_token = get_access_token()  # هنا يتم التجديد التلقائي
    url = f"{settings.ZOHO_API_DOMAIN}/api/accounts/{settings.ZOHO_ACCOUNT_ID}/messages"
    headers = {
        "Authorization": f"Zoho-oauthtoken {access_token}",
        "Content-Type": "application/json"
    }
    data = {
        "fromAddress": settings.ZOHO_FROM_EMAIL,
        "toAddress": to,
        "subject": subject,
        "content": content,
        "contentType": "html"
    }
    response = requests.post(url, json=data, headers=headers, timeout=10)
    response.raise_for_status()
    return response.json()
