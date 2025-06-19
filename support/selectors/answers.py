from support.models import SupportAnswer


def get_answers_for_message(message_id: int):
    support_messages = SupportAnswer.objects.filter(message=message_id)

    return support_messages
