from django.db import models
class SiteSetting(models.Model):
    store_name = models.CharField(max_length=150, default="تک‌استور", verbose_name="نام فروشگاه")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "تنظیمات سایت"
        verbose_name_plural = "تنظیمات سایت"

    def __str__(self):
        return self.store_name

    @classmethod
    def get_store_name(cls):
        try:
            instance = cls.objects.first()
            return instance.store_name if instance else "تک‌استور"
        except Exception:
            return "تک‌استور"

    @classmethod
    def get_settings(cls):
        try:
            instance, _ = cls.objects.get_or_create(pk=1, defaults={"store_name": "تک‌استور"})
            return instance
        except Exception:
            return None