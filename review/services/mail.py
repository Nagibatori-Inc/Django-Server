from django.template.loader import render_to_string

from notification.tasks import send_email_task
from review.models import Review


REVIEW_MODERATIOIN_RESULT_MESSAGE_SUBJECT = 'Результаты модерации письма'


def send_message_about_moderation_results(is_review_approved: bool, review: Review) -> None:
    """Отправить письмо о результатах модерации отзыва пользователю"""
    html_message = render_to_string(
        'mail/review_moderation_result_mail.html',
        context={'profile_name': review.profile.name, 'is_review_approved': is_review_approved},
    )
    send_email_task(
        subject=REVIEW_MODERATIOIN_RESULT_MESSAGE_SUBJECT,
        html_message=html_message,
        email=review.author.user.email,
    )
