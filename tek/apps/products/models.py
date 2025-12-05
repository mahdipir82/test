import os
from uuid import uuid4
from datetime import datetime
from django.db import models
from django.utils import timezone
from django.urls import reverse
from django.db.models import Sum
from utils import FileUpload


# ================================
# Brand
# ================================
class Brand(models.Model):
    title = models.CharField(max_length=100, verbose_name='نام برند')
    slug = models.SlugField(max_length=200, unique=True, verbose_name='اسلاگ')

    file_upload = FileUpload('images', 'brands')
    image = models.ImageField(
        upload_to=file_upload.upload_to,
        blank=True,
        null=True,
        verbose_name="تصویر برند"
    )

    description = models.TextField(blank=True, null=True, verbose_name="توضیحات برند")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'برند'
        verbose_name_plural = 'برندها'


# ================================
# Category
# ================================
class Category(models.Model):
    title = models.CharField(max_length=120, verbose_name="نام دسته")
    slug = models.SlugField(max_length=200, unique=True, verbose_name='اسلاگ')
    description = models.TextField(blank=True, null=True, verbose_name="توضیحات")

    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='subcategories',
        verbose_name="دسته والد"
    )

    file_upload = FileUpload('images', 'categories')
    image = models.ImageField(upload_to=file_upload.upload_to, blank=True, null=True, verbose_name="تصویر دسته")

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'دسته‌بندی'
        verbose_name_plural = 'دسته‌بندی‌ها'


# ================================
# ویژگی کالا
# ================================
class Feature(models.Model):
    feature_name = models.CharField(max_length=100, verbose_name='نام ویژگی')
    product_group = models.ManyToManyField(Category, verbose_name="گروه کالا", related_name='features')

    def __str__(self):
        return self.feature_name

    class Meta:
        verbose_name = 'ویژگی'
        verbose_name_plural = 'ویژگی‌ها'


# ================================
# مقدار ویژگی‌ها
# ================================
class FeatureValue(models.Model):
    value_title = models.CharField(max_length=100, null=True, verbose_name='عنوان مقدار')
    feature = models.ForeignKey(Feature, on_delete=models.CASCADE, related_name="values", verbose_name="ویژگی")

    def __str__(self):
        return f"{self.feature.feature_name}: {self.value_title}"

    class Meta:
        verbose_name = 'مقدار ویژگی'
        verbose_name_plural = 'مقادیر ویژگی‌ها'

# ================================
# Product
# ================================
class Product(models.Model):
    name = models.CharField(max_length=250, verbose_name="نام کالا")
    slug = models.SlugField(max_length=250, unique=True, verbose_name="اسلاگ")
    description = models.TextField(blank=True, null=True, verbose_name="توضیحات")

    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    categories = models.ManyToManyField(Category, related_name='products')

    file_upload = FileUpload('images', 'products')
    main_image = models.ImageField(upload_to=file_upload.upload_to, blank=True, null=True, verbose_name="تصویر اصلی")

    price = models.PositiveIntegerField(default=0, verbose_name="قیمت")
    stock = models.PositiveIntegerField(default=0, verbose_name="موجودی")
    is_active = models.BooleanField(default=True, verbose_name="فعال / غیرفعال")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("api:product-detail", kwargs={"slug": self.slug})

    def get_price_after_discount(self):
        """در آینده از اپ discounts صدا زده می‌شود"""
        return self.price

    class Meta:
        verbose_name = 'کالا'
        verbose_name_plural = 'کالاها'

class ProductFeature(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='کالا', related_name='product_features')
    feature = models.ForeignKey(Feature, on_delete=models.CASCADE, verbose_name="ویژگی")
    value = models.CharField(max_length=100, verbose_name='مقدار ویژگی کالا')
    filter_value = models.ForeignKey(
        FeatureValue,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        verbose_name='مقدار ویژگی برای فیلتر',
        related_name='products_with_value'
    )

    def __str__(self):
        return f"{self.product} - {self.feature}: {self.value}"

    class Meta:
        verbose_name = 'ویژگی محصول'
        verbose_name_plural = 'ویژگی‌های محصولات'


# ================================
# Product Gallery
# ================================
class ProductGallery(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='gallery_images')
    file_upload = FileUpload('images', 'gallery')
    image = models.ImageField(upload_to=file_upload.upload_to, verbose_name='تصویر')

    def __str__(self):
        return f"تصویر {self.product.name}"

    class Meta:
        verbose_name = 'گالری محصول'
        verbose_name_plural = 'گالری محصولات'




class ProductColor(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='colors')
    color_name = models.CharField(max_length=50, verbose_name='رنگ')
    color_code = models.CharField(max_length=7, blank=True, null=True, verbose_name='کد رنگ HEX')  # مثلا #000000
    image = models.ImageField(upload_to='images/product_colors/', blank=True, null=True, verbose_name='تصویر رنگ')

    def __str__(self):
        return f"{self.product.name} - {self.color_name}"

    class Meta:
        verbose_name = 'رنگ محصول'
        verbose_name_plural = 'رنگ‌های محصول'