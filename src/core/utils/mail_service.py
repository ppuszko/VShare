from fastapi.requests import Request
from fastapi import BackgroundTasks
from fastapi_mail import MessageSchema, MessageType, NameEmail
from jinja2 import Environment, FileSystemLoader, select_autoescape
from enum import Enum

email_templates = Environment(
    loader=FileSystemLoader("src/templates/email"),
    autoescape=select_autoescape(["html", "xml"])
)

class EmailType(Enum):
    CONFIRMATION = ("E-mail confirmation", "confirm-email.html")
    INVITE = ("Group invitation", "redeem-invite.html")
    EMBEDDING_REPORT = ("Embedding process report", "embedding-report.html")

    def __init__(self, subject: str, template: str):
        self.subject = subject
        self.template = template

def get_mailing_service(request: Request):
    return MailService(request)

class MailService:
    # TODO: swap request to Dependency Injection 
    def __init__(self, request: Request):
        self._fastmail = request.app.state.fastmail


    async def send_templated_email(self, context: dict, recipients: list[str], email_type: EmailType, background_tasks: BackgroundTasks):
        subject = email_type.subject
        body = self._render_template(email_type.template, context)
        
        await self._send_email(subject, body, recipients, background_tasks)


    async def _send_email(self, subject: str, body: str, recipients: list[str], background_tasks: BackgroundTasks):
        message = MessageSchema(subject=subject,
                                recipients=[NameEmail("", email) for email in recipients],
                                body=body,
                                subtype=MessageType.html)

        background_tasks.add_task(self._fastmail.send_message, message)        


    def _render_template(self, name: str, context: dict):
        template = email_templates.get_template(name)
        return template.render(**context)