from django.contrib import admin
from .models import Warehouse, Stock, StockMovement
from apps.products.models import Product

@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ("name", "location", "created_at")
    search_fields = ("name", "location")
    list_filter = ("created_at",)
    ordering = ("-created_at",)


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ("product", "warehouse", "quantity")
    list_filter = ("warehouse",)
    search_fields = ("product__name",)
    verbose_name = "موجودی محصول"
    verbose_name_plural = "موجودی محصولات"


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ("product", "warehouse", "movement_type", "quantity", "created_at")
    list_filter = ("movement_type", "warehouse")
    search_fields = ("product__name",)
    readonly_fields = ("created_at",)
    fieldsets = (
        ("اطلاعات اصلی", {"fields": ("product", "warehouse", "movement_type", "quantity", "description")}),
        ("تاریخ و زمان", {"fields": ("created_at",)}),
    )

    def save_model(self, request, obj, form, change):
        # ذخیره و بروزرسانی موجودی محصول
        super().save_model(request, obj, form, change)
