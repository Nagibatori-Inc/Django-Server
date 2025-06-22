from DjangoServer import celery_app
from notification.services.mail import send_mail
from notification.services.sms import sms_service


@celery_app.task
def send_email_task(subject: str, html_message: str, email: str):
    send_mail(subject=subject, html_message=html_message, email=email)


def send_sms_task(phone: str, text: str, **kwargs):
    sms_service.send_message(phone, text, **kwargs)
