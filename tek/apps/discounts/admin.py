from django.contrib import admin
from .models import DiscountBasket

@admin.register(DiscountBasket)
class DiscountBasketAdmin(admin.ModelAdmin):
    list_display = ("title", "discount_type", "discount", "is_active", "start_date", "end_date")
    list_filter = ("discount_type", "is_active", "start_date", "end_date")
    search_fields = ("title", "code")
    filter_horizontal = ("products", "groups", "brands", "users")  # انتخاب چندتایی راحت
    ordering = ("-start_date",)
    fieldsets = (
        (None, {
            "fields": ("title", "discount_type", "discount", "code", "is_active")
        }),
        ("زمان‌بندی و محدودیت", {
            "fields": ("start_date", "end_date", "min_purchase_amount", "max_discount_amount")
        }),
        ("اعمال روی", {
            "fields": ("products", "groups", "brands", "users")
        }),
    )

    def get_queryset(self, request):
        # نمایش تخفیف‌های فعال در ابتدای لیست
        qs = super().get_queryset(request)
        return qs.order_by("-is_active", "-start_date")
