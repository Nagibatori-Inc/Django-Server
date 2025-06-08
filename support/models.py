from django.contrib.auth.models import User
from django.db import models


class SupportMessage(models.Model):
    user = models.ForeignKey(
        User,
        related_name="support_messages",
        on_delete=models.DO_NOTHING,
        verbose_name="Пользователь",
    )
    subject = models.CharField(max_length=100, verbose_name="Тема обращения")
    message = models.TextField(verbose_name="Текст сообщения")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата отправки")
    is_resolved = models.BooleanField(default=False, verbose_name="Решено")

    class Meta:
        verbose_name = "Сообщение в поддержку"
        verbose_name_plural = "Сообщения в поддержку"
        ordering = ["-created_at"]

    def __str__(self):
        return f"[{self.user}] {self.subject}"


class SupportAnswer(models.Model):
    message = models.ForeignKey(
        SupportMessage, related_name="answers", on_delete=models.DO_NOTHING, verbose_name="Обращение"
    )
    answer = models.TextField(verbose_name="Ответ")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата отправки")

    class Meta:
        verbose_name = "Ответ поддержки"
        verbose_name_plural = "Ответы поддержки"
        ordering = ["-created_at"]
