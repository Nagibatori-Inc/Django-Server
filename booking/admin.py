from django.contrib import admin

from booking.models import Advert, Promotion, AdvertImage


@admin.register(Advert)
class AdvertAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'price', 'created_at', 'status', 'activated_at', 'logo']
    search_fields = ['title', 'contact__name', 'price']
    list_filter = ['created_at', 'activated_at', 'status']
    readonly_fields = ['contact', 'images']

    @admin.display(description='Фотографии')
    def images(self, obj):
        return obj.images if obj.images else ''


@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    list_display = ['type', 'rate']
    search_fields = ['type', 'rate']
    list_filter = ['rate']


@admin.register(AdvertImage)
class AdvertImageAdmin(admin.ModelAdmin):
    list_display = ['image']
