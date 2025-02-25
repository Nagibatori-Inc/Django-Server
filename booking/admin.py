from django.contrib import admin

from booking.models import Advert, Promotion


@admin.register(Advert)
class AdvertAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'contact_id', 'price', 'created_at', 'activated_at', 'status']
    search_fields = ['title', 'contact__name', 'price']
    list_filter = ['created_at', 'activated_at', 'status']
    readonly_fields = ['contact']
    
    
@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    list_display = ['type', 'rate']
    search_fields = ['type', 'rate']
    list_filter = ['rate']
