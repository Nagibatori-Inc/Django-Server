from django.contrib import admin

from payments.models import Payment


class PaymentAdmin(admin.ModelAdmin):
    search_fields = ["user__username"]
    list_display = ["user", "advert", "amount", "status", "created_at"]
    list_filter = ["status"]


admin.site.register(Payment, PaymentAdmin)
