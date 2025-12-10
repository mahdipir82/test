from rest_framework import serializers
from apps.products.models import Brand, Category, Product, ProductGallery,ProductColor
from django.utils import timezone
from django.db import models
from apps.warehouse.models import Stock  
from rest_framework.response import Response
class ProductColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductColor
        fields = ('id', 'color_name', 'color_code', 'image')
class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = '__all__'


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class ProductGallerySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductGallery
        fields = ['id', 'image']


from rest_framework import serializers
from django.utils import timezone
from decimal import Decimal
from apps.products.models import Product
from apps.discounts.models import DiscountBasket  # اضافه شده
from .models import Brand, Category
from .serializers import BrandSerializer, CategorySerializer, ProductGallerySerializer

class ProductSerializer(serializers.ModelSerializer):
    brand = BrandSerializer(read_only=True)
    categories = CategorySerializer(many=True, read_only=True)
    features = serializers.SerializerMethodField()
    discount = serializers.SerializerMethodField()
    originalPrice = serializers.SerializerMethodField()
    finalPrice = serializers.SerializerMethodField()
    main_image = serializers.SerializerMethodField()
    colors = ProductColorSerializer(many=True, read_only=True)
    gallery_images = ProductGallerySerializer(many=True, read_only=True)
    stock_quantity = serializers.SerializerMethodField()  # 👈 اضافه شده

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'description', 'price', 'main_image',
            'brand', 'categories', 'colors', 'features',
            'discount', 'originalPrice', 'finalPrice',
            'stock_quantity', 'gallery_images'  # 👈 اضافه شد
        ]

    def get_features(self, obj):
        features = {}
        for pf in obj.product_features.all():
            name = pf.feature.feature_name
            if name not in features:
                features[name] = []
            if pf.value not in features[name]:
                features[name].append(pf.value)
        return features

    def get_discount(self, obj):
        now = timezone.now()
        active_discounts = obj.discount_baskets.filter(
            is_active=True,
            start_date__lte=now
        ).filter(
            models.Q(end_date__gte=now) | models.Q(end_date__isnull=True)
        )

        if not active_discounts.exists():
            return 0

        max_discount_amount = Decimal('0.00')
        for d in active_discounts:
            if not d.is_valid():
                continue
            discount_amount = d.apply_discount_to_product(obj)
            if discount_amount > max_discount_amount:
                max_discount_amount = discount_amount

        return round(max_discount_amount, 2)

    def get_originalPrice(self, obj):
        return obj.price

    def get_finalPrice(self, obj):
        discount_amount = Decimal(self.get_discount(obj))
        return max(obj.price - discount_amount, Decimal('0.00'))

    def get_main_image(self, obj):
        request = self.context.get('request')
        if obj.main_image:
            return request.build_absolute_uri(obj.main_image.url) if request else obj.main_image.url
        return None

    def get_stock_quantity(self, obj):
        """جمع موجودی محصول در تمام انبارها"""
        return Stock.objects.filter(product=obj).aggregate(total=models.Sum('quantity'))['total'] or 0


