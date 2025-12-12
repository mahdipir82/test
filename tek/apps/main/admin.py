from django.contrib import admin

from .models import SiteSetting


@admin.register(SiteSetting)
class SiteSettingAdmin(admin.ModelAdmin):
    list_display = ("store_name", "updated_at")
    readonly_fields = ("updated_at",)
