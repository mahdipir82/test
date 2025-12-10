from django.contrib import admin
from django.utils.html import format_html
from .models import ProductReview
from .models import (
    Brand, Category, Feature,FeatureValue,
    Product, ProductFeature,ProductGallery,ProductColor
)

# ================================
# Inline برای رنگ‌های محصول
# ================================
class ProductColorInline(admin.TabularInline):
    model = ProductColor
    extra = 1
    readonly_fields = ('color_preview',)

    def color_preview(self, obj):
        if obj.color_code:
            return format_html(
                '<div style="width:30px; height:30px; background-color:{}; border-radius:50%; border:1px solid #ccc;"></div>',
                obj.color_code
            )
        elif obj.image:
            return format_html('<img src="{}" width="30" height="30" style="border-radius:50%;">', obj.image.url)
        return "—"
    color_preview.short_description = "پیش‌نمایش رنگ"

# ============================
# 📘 Brand Resource
# ============================

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'image')
    search_fields = ('title',)
    prepopulated_fields = {'slug': ('title',)}

    def image_tag(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="border-radius:8px;">', obj.image.url)
        return "—"
    image_tag.short_description = 'تصویر برند'


# ============================
# 📘 Product Group Resource
# ============================

@admin.register(Category)
class ProductGroupAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active', 'parent', 'slug', 'image')
    list_filter = ('is_active',)
    search_fields = ('title', 'description')
    prepopulated_fields = {'slug': ('title',)}

    def image_tag(self, obj):
        if obj.image_name:
            return format_html('<img src="{}" width="50" height="50" style="border-radius:8px;">', obj.image_name.url)
        return "—"
    image_tag.short_description = 'تصویر گروه'


# ============================
# 📘 Feature + FeatureValue
# ============================
class FeatureValueInline(admin.TabularInline):
    model = FeatureValue
    extra = 1


@admin.register(Feature)
class FeatureAdmin(admin.ModelAdmin):
    list_display = ('feature_name',)
    search_fields = ('feature_name',)
    filter_horizontal = ('product_group',)
    inlines = [FeatureValueInline]


# ============================
# 📘 Product Resource
# ============================


class ProductFeatureInline(admin.TabularInline):
    model = ProductFeature
    extra = 1


class ProductGalleryInline(admin.TabularInline):
    model = ProductGallery
    extra = 1
    readonly_fields = ('image_preview',)

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="60" height="60" style="border-radius:8px;">', obj.image.url)
        return "—"
    image_preview.short_description = "پیش‌نمایش تصویر"


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'brand', 'price', 'is_active', 'get_categories', 'thumbnail')
    list_filter = ('is_active', 'brand', 'categories')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductFeatureInline, ProductGalleryInline, ProductColorInline]
    readonly_fields = ('created_at', 'updated_at')

    def get_categories(self, obj):
        return "، ".join([c.title for c in obj.categories.all()])
    get_categories.short_description = 'دسته‌بندی‌ها'

    def thumbnail(self, obj):
        if obj.main_image:
            return format_html('<img src="{}" width="60" height="60" style="border-radius:8px;">', obj.main_image.url)
        return "—"
    thumbnail.short_description = 'تصویر'

    fieldsets = (
        ('اطلاعات اصلی', {
            'fields': ('name', 'slug', 'description', 'brand', 'categories', 'is_active')
        }),
        ('قیمت و تصویر', {
            'fields': ('price', 'main_image')
        }),
        ('تاریخ‌ها', {
            'fields': ('created_at', 'updated_at')
        }),
    )


# ============================
# 📘 Product Gallery Admin
# ============================
@admin.register(ProductGallery)
class ProductGalleryAdmin(admin.ModelAdmin):
    list_display = ('product', 'image_preview')
    search_fields = ('product__name',)

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="60" height="60" style="border-radius:8px;">', obj.image.url)
        return "—"
    image_preview.short_description = 'تصویر'



@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'name', 'rating', 'is_approved', 'created_at')
    list_filter = ('is_approved', 'rating', 'created_at')
    search_fields = ('product__name', 'name', 'email', 'comment')
    actions = ['approve_reviews']

    @admin.action(description='تایید نظرات انتخاب شده')
    def approve_reviews(self, request, queryset):
        queryset.update(is_approved=True)