from django.contrib import admin
from django.forms.widgets import Textarea

from support.models import SupportMessage, SupportAnswer


@admin.action(description='Пометить как решенный')
def make_resolved(modeladmin, request, queryset):
    queryset.update(is_resolved=True)


@admin.register(SupportMessage)
class SupportMessageAdmin(admin.ModelAdmin):

    search_fields = ['user']
    list_display = ['user', 'subject', 'short_message', 'created_at', 'is_resolved']
    readonly_fields = ['subject', 'created_at', 'is_resolved']
    list_filter = ['is_resolved']
    actions = [make_resolved]

    def get_form(self, request, obj=None, **kwargs):
        form = super(SupportMessageAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields['message'].widget = Textarea(attrs={'rows': 20, 'cols': 50})
        form.base_fields['message'].disabled = True
        return form

    @admin.display(description='Текст сообщения')
    def short_message(self, obj: SupportMessage) -> str:
        if len(obj.message) > 100:
            return obj.message[:100] + '...'
        return obj.message


@admin.register(SupportAnswer)
class SupportAnswerAdmin(admin.ModelAdmin):

    list_display = ['message', 'short_answer', 'created_at']
    readonly_fields = ['agent', 'message', 'created_at']
    list_filter = ['message']

    def get_form(self, request, obj=None, **kwargs):
        form = super(SupportAnswerAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields['answer'].widget = Textarea(attrs={'rows': 20, 'cols': 50})
        form.base_fields['answer'].disabled = True
        return form

    @admin.display(description='Текст ответа')
    def short_answer(self, obj: SupportAnswer) -> str:
        if len(obj.answer) > 100:
            return obj.answer[:100] + '...'
        return obj.answer
