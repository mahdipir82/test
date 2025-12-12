from .models import SiteSetting


def site_settings(request):
    try:
        settings_obj = SiteSetting.get_settings()
    except Exception:
        settings_obj = None
    return {
        "site_settings": settings_obj,
        "store_name": settings_obj.store_name if settings_obj else "تک‌استور",
    }