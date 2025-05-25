from DjangoServer import celery_app
from notification.services.mail import send_mail


@celery_app.task
def send_email_task(subject: str, html_message: str, email: str):
    send_mail(subject=subject, html_message=html_message, email=email)
