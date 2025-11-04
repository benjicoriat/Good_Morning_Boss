import smtplib
import ssl
from email.message import EmailMessage
from typing import Dict

def send_email_report(pdf_path: str, date_str: str, api_keys: Dict):
    msg = EmailMessage()
    msg['Subject'] = f'Good Morning Boss Report {date_str}'
    msg['From'] = api_keys['SMTP_USER']
    msg['To'] = api_keys['EMAIL_TO']
    msg.set_content('Please find attached the daily portfolio report.')
    with open(pdf_path, 'rb') as f:
        data = f.read()
    msg.add_attachment(data, maintype='application', subtype='pdf', filename=pdf_path)
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(api_keys['SMTP_SERVER'], int(api_keys['SMTP_PORT']), context=context) as server:
        server.login(api_keys['SMTP_USER'], api_keys['SMTP_PASSWORD'])
        server.send_message(msg)