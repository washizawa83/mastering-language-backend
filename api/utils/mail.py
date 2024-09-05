import os
from dotenv import load_dotenv
import smtplib, ssl
from email.mime.text import MIMEText


load_dotenv()

def create_mail(
    subject: str,
    message_to: str,
    message_body: str
):
    message = MIMEText(message_body)
    message['Subject'] = subject
    message['From'] = os.environ.get('FROM_MAIL_ADDRESS')
    message['To'] = message_to

    return message

def send_mail(message: MIMEText):
    smtp = smtplib.SMTP_SSL("smtp.gmail.com", 465, context = ssl.create_default_context())

    smtp.login(os.environ.get('FROM_MAIL_ADDRESS'), os.environ.get('APP_PASSWORD'))
    smtp.send_message(message)
    smtp.close()