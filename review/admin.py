from django.contrib import admin
from django.forms.widgets import Textarea

from review.models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """Админка для модели Review"""

    list_display = ['profile_name', 'author_name', 'short_text', 'created_at', 'is_approved', 'approved_by']
    readonly_fields = ['rate', 'approved_by', 'created_at']
    list_filter = ['is_approved', 'approved_by']

    def get_form(self, request, obj=None, **kwargs):
        """Изменение виджета поля text"""
        form = super(ReviewAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields['text'].widget = Textarea(attrs={'rows': 20, 'cols': 50})
        form.base_fields['text'].disabled = True
        return form

    @admin.display(description='Профиль')
    def profile_name(self, obj: Review) -> str:
        return obj.profile.name

    @admin.display(description='Автор отзыва')
    def author_name(self, obj: Review) -> str:
        return obj.author.name

    @admin.display(description='Текст отзыва')
    def short_text(self, obj: Review) -> str:
        if len(obj.text) > 100:
            return obj.text[:100] + '...'
        return obj.text
