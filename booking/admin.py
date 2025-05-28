from django.contrib import admin

from booking.models import Advert, Promotion


@admin.register(Advert)
class AdvertAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'price', 'created_at', 'status', 'activated_at']
    search_fields = ['title', 'contact__name', 'price']
    list_filter = ['created_at', 'activated_at', 'status']


@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    list_display = ['type', 'rate']
    search_fields = ['type', 'rate']
    list_filter = ['rate']
