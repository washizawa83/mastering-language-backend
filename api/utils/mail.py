import os
import smtplib, ssl
from email.mime.text import MIMEText
from typing import Callable, Awaitable
from functools import wraps

from dotenv import load_dotenv
from pydantic import BaseModel

import api.models.auth as auth_model


load_dotenv()

SSL_PORT = 465


class Message(BaseModel):
    subject: str
    message_to: str
    message_body: str


def create_message(message: Message):
    mime_text = MIMEText(message.message_body)
    mime_text['Subject'] = message.subject
    mime_text['From'] = os.environ.get('FROM_MAIL_ADDRESS')
    mime_text['To'] = message.message_to

    return mime_text


def send_mail(message: MIMEText):
    smtp = smtplib.SMTP_SSL(
        'smtp.gmail.com', SSL_PORT, context=ssl.create_default_context()
    )
    smtp.login(
        os.environ.get('FROM_MAIL_ADDRESS'), os.environ.get('APP_PASSWORD')
    )
    smtp.send_message(message)
    smtp.close()


def after_verification_send_mail_decorator(
    func: Callable[..., Awaitable[auth_model.Verification]],
) -> Callable[..., Awaitable[auth_model.Verification]]:
    @wraps(func)
    async def wrapper(*args, **kwargs):
        result = await func(*args, **kwargs)
        message_create = Message(
            subject='Verification Code',
            message_to=result.email,
            message_body=f'Your verification code is {result.verification_code}',
        )
        message = create_message(message_create)
        send_mail(message)

        return result

    return wrapper
