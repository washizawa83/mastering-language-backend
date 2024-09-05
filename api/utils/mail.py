import os
from dotenv import load_dotenv
import smtplib, ssl
from email.mime.text import MIMEText
from functools import wraps

from pydantic import BaseModel


load_dotenv()

class MessageCreate(BaseModel):
    subject: str
    message_to: str
    message_body: str

def create_message(message_create: MessageCreate):
    message = MIMEText(message_create.message_body)
    message['Subject'] = message_create.subject
    message['From'] = os.environ.get('FROM_MAIL_ADDRESS')
    message['To'] = message_create.message_to

    return message

def send_mail(message: MIMEText):
    smtp = smtplib.SMTP_SSL("smtp.gmail.com", 465, context = ssl.create_default_context())

    smtp.login(os.environ.get('FROM_MAIL_ADDRESS'), os.environ.get('APP_PASSWORD'))
    smtp.send_message(message)
    smtp.close()


def after_verification_send_mail_decorator(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        result = await func(*args, **kwargs)

        message_create = MessageCreate(
            subject="Verification Code",
            message_to=result.email,
            message_body=f"Your verification code is {result.verification_code}"
        )
        message = create_message(message_create)
        send_mail(message)

        return result

    return wrapper