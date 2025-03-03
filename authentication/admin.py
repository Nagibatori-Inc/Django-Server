from django.contrib import admin

from authentication.models import Profile, OneTimePassword


# Register your models here.
class ProfileAdmin(admin.ModelAdmin):
    search_fields = ["name", "user__username"]
    list_display = ["user", "name", "type", "is_deleted"]
    list_filter = ["is_deleted", "type"]


class OTPAdmin(admin.ModelAdmin):
    readonly_fields = ["code"]
    search_fields = ["user__username"]
    list_display = ["user", "creation_date", "has_expired"]


admin.site.register(Profile, ProfileAdmin)
admin.site.register(OneTimePassword, OTPAdmin)
