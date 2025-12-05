from django.db import models
from django.utils import timezone
from apps.products.models import Product  # محصولات اصلی

class Warehouse(models.Model):
    name = models.CharField("نام انبار", max_length=100)
    location = models.TextField("مکان", blank=True)
    created_at = models.DateTimeField("تاریخ ایجاد", auto_now_add=True)

    class Meta:
        verbose_name = "انبار"
        verbose_name_plural = "انبارها"

    def __str__(self):
        return self.name


class Stock(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="محصول", related_name="stocks")
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, verbose_name="انبار", related_name="stocks")
    quantity = models.PositiveIntegerField("موجودی", default=0)

    class Meta:
        unique_together = ('product', 'warehouse')
        verbose_name = "موجودی محصول"
        verbose_name_plural = "موجودی محصولات"

    def __str__(self):
        return f"{self.product.name} - {self.warehouse.name}"


class StockMovement(models.Model):
    IN = 'in'
    OUT = 'out'
    MOVEMENT_TYPE = [
        (IN, 'ورود'),
        (OUT, 'خروج'),
    ]
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="محصول")
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, verbose_name="انبار")
    movement_type = models.CharField("نوع تراکنش", max_length=3, choices=MOVEMENT_TYPE)
    quantity = models.PositiveIntegerField("تعداد")
    description = models.TextField("توضیحات", blank=True)
    created_at = models.DateTimeField("تاریخ تراکنش", default=timezone.now)

    class Meta:
        verbose_name = "تراکنش موجودی"
        verbose_name_plural = "تراکنش‌های موجودی"
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        stock, created = Stock.objects.get_or_create(product=self.product, warehouse=self.warehouse)
        if self.movement_type == self.IN:
            stock.quantity += self.quantity
        else:
            stock.quantity -= self.quantity
            if stock.quantity < 0:
                stock.quantity = 0
        stock.save()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.get_movement_type_display()} {self.quantity} - {self.product.name}"
