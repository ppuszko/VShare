from fastapi_mail import FastMail, ConnectionConfig, MessageSchema, MessageType, NameEmail
from pydantic import SecretStr
from fastapi import BackgroundTasks
from fastapi.requests import Request


async def send_mail_background(subject: str, recipients: list[NameEmail], body: str, request: Request, background_tasks: BackgroundTasks):
    message = MessageSchema(subject=subject, 
                            recipients=recipients,
                            body=body,
                            subtype=MessageType.html)
    
    background_tasks.add_task(request.app.state.fastmail.send_message, message)

def generate_confirmation_template(username: str, link: str) -> str:
    return f"""
    <h1>Verify your email</h1>
    <p>Hi {username}! 
    </br> Please click this <a href="{link}">link</a> to verify your email.
    This activation link will expire in 20 minutes.</p>
    """