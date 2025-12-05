from rest_framework import serializers
from .models import DiscountBasket
from apps.products.models import Product
from apps.accounts.models import CustomUser
from decimal import Decimal
from django.utils import timezone
from django.db import models

class DiscountApplySerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    user_id = serializers.IntegerField(required=False, allow_null=True)
    code = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    final_price = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    discount_amount = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    discount_type = serializers.CharField(read_only=True)  # نوع تخفیف
    discount_percentage = serializers.DecimalField(max_digits=5, decimal_places=2, read_only=True)  # درصد تخفیف

    def get_discounted_price(self):
        product_id = self.validated_data.get("product_id")
        user_id = self.validated_data.get("user_id")
        code = self.validated_data.get("code")

        try:
            product = Product.objects.get(pk=product_id)
        except Product.DoesNotExist:
            raise serializers.ValidationError("محصول یافت نشد.")

        user = None
        if user_id:
            try:
                user = CustomUser.objects.get(pk=user_id)
            except CustomUser.DoesNotExist:
                raise serializers.ValidationError("کاربر یافت نشد.")

        now = timezone.now()
        discounts = product.discount_baskets.filter(is_active=True, start_date__lte=now).filter(
            models.Q(end_date__gte=now) | models.Q(end_date__isnull=True)
        )

        # فیلتر کاربر
        if user:
            user_discounts = discounts.filter(users=user)
            if user_discounts.exists():
                discounts = user_discounts

        # فیلتر کد تخفیف
        if code:
            discounts = discounts.filter(code=code)

        if not discounts.exists():
            return product.price, Decimal("0.00"), None, Decimal("0.00")

        best_discount = discounts.order_by('-discount').first()

        if best_discount.discount_type == 'percentage':
            discount_amount = product.price * (best_discount.discount / Decimal('100'))
            discount_percentage = best_discount.discount
            if best_discount.max_discount_amount:
                discount_amount = min(discount_amount, best_discount.max_discount_amount)
        else:
            discount_amount = best_discount.discount
            discount_percentage = (best_discount.discount / product.price * Decimal('100')).quantize(Decimal('0.01'))

        final_price = max(product.price - discount_amount, Decimal('0.00'))
        return final_price, discount_amount, best_discount.discount_type, discount_percentage

    def validate(self, attrs):
        final_price, discount_amount, discount_type, discount_percentage = self.get_discounted_price()
        attrs['final_price'] = final_price
        attrs['discount_amount'] = discount_amount
        attrs['discount_type'] = discount_type
        attrs['discount_percentage'] = discount_percentage
        return attrs
