from django.db import models
from django.utils import timezone
from apps.products.models import Product, Category, Brand
from apps.accounts.models import CustomUser
from decimal import Decimal

class DiscountType(models.TextChoices):
    PERCENTAGE = 'percentage', 'درصدی'
    FIXED = 'fixed', 'مبلغ ثابت'

class DiscountBasket(models.Model):
    title = models.CharField(max_length=200, verbose_name="عنوان تخفیف")
    discount_type = models.CharField(
        max_length=20,
        choices=DiscountType.choices,
        default=DiscountType.PERCENTAGE,
        verbose_name="نوع تخفیف"
    )
    discount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="مقدار تخفیف (درصد یا مبلغ)"
    )
    start_date = models.DateTimeField(default=timezone.now, verbose_name="تاریخ شروع")
    end_date = models.DateTimeField(null=True, blank=True, verbose_name="تاریخ پایان")
    min_purchase_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True, blank=True,
        verbose_name="حداقل مبلغ خرید"
    )
    max_discount_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True, blank=True,
        verbose_name="حداکثر مبلغ تخفیف (در صورت درصدی)"
    )
    is_active = models.BooleanField(default=True, verbose_name="فعال / غیرفعال")

    products = models.ManyToManyField(Product, blank=True, related_name="discount_baskets", verbose_name="کالاها")
    groups = models.ManyToManyField(Category, blank=True, related_name="discount_baskets", verbose_name="گروه‌ها")
    brands = models.ManyToManyField(Brand, blank=True, related_name="discount_baskets", verbose_name="برندها")
    users = models.ManyToManyField(CustomUser, blank=True, related_name="discount_baskets", verbose_name="کاربران خاص")

    code = models.CharField(max_length=50, blank=True, null=True, unique=True, verbose_name="کد تخفیف (اختیاری)")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="آخرین بروزرسانی")

    class Meta:
        verbose_name = "سبد تخفیف"
        verbose_name_plural = "سبدهای تخفیف"
        ordering = ['-created_at']

    def __str__(self):
        symbol = '%' if self.discount_type == DiscountType.PERCENTAGE else 'تومان'
        return f"{self.title} ({self.discount}{symbol})"

    def is_valid(self):
        now = timezone.now()
        if not self.is_active:
            return False
        if self.start_date > now:
            return False
        if self.end_date and now > self.end_date:
            return False
        return True

    def calculate_discount(self, amount: Decimal):
        if not self.is_valid():
            return Decimal('0.00')

        discount_amount = Decimal('0.00')
        if self.discount_type == DiscountType.PERCENTAGE:
            discount_amount = amount * (self.discount / Decimal('100'))
            if self.max_discount_amount:
                discount_amount = min(discount_amount, self.max_discount_amount)
        elif self.discount_type == DiscountType.FIXED:
            discount_amount = self.discount

        if self.min_purchase_amount and amount < self.min_purchase_amount:
            return Decimal('0.00')

        return discount_amount

    def apply_discount_to_product(self, product: Product, user: CustomUser = None):
        if not self.is_valid():
            return Decimal('0.00')

        if self.users.exists() and user not in self.users.all():
            return Decimal('0.00')

        if self.products.exists() and product not in self.products.all():
            return Decimal('0.00')
        if self.groups.exists() and not any(g in self.groups.all() for g in product.categories.all()):
            return Decimal('0.00')
        if self.brands.exists() and product.brand not in self.brands.all():
            return Decimal('0.00')

        return self.calculate_discount(product.price)
