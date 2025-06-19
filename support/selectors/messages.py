from django.contrib.auth.models import User
from rest_framework.exceptions import ValidationError

from support.models import SupportMessage


def get_user_messages(user: User):
    support_messages = SupportMessage.objects.filter(user=user)

    return support_messages


def get_message_by_id(message_id: int):
    try:
        message = SupportMessage.objects.get(pk=message_id)
    except SupportMessage.DoesNotExist:
        raise ValidationError("Нет такого сообщения")

    return message
