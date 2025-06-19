from django.contrib.auth.models import User

from support.models import SupportMessage


def get_user_messages(user: User):
    support_messages = SupportMessage.objects.filter(user=user)

    return support_messages
