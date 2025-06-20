from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags


def send_mail(subject: str, html_message: str, email: str):
    """Отправить письмо пользователю на почту"""
    text_message = strip_tags(html_message)
    mail = EmailMultiAlternatives(
        subject=subject,
        body=text_message,
        from_email=settings.EMAIL_HOST_USER,
        to=[email],
    )
    mail.attach_alternative(html_message, "text/html")
    mail.send()
