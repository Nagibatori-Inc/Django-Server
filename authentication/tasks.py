from DjangoServer import celery_app
from authentication.services.sms import sms_service


@celery_app.task
def send_sms_wrapper(phone: str, text: str, **kwargs):
    sms_service.send_message(phone, text, **kwargs)
