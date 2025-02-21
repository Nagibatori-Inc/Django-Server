from django.contrib import admin

from authentication.models import Profile, OneTimePassword


# Register your models here.


class ProfileAdmin(admin.ModelAdmin):
    search_fields = ["name", "user__username"]
    list_display = ["name", "user", "type", "is_deleted"]
    list_filter = ["is_deleted", "type"]


admin.site.register(Profile, ProfileAdmin)
admin.site.register(OneTimePassword)