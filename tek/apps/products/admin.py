from django.contrib import admin
from django.utils.html import format_html

from .models import (
    Brand,
    Category,
    Feature,
    FeatureValue,
    Product,
    ProductFeature,
    ProductGallery,
    ProductColor,
    ProductReview,
    ProductReviewReply,
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
    list_display = ('product', 'name', 'rating_stars', 'status_badge', 'created_at')
    list_filter = ('is_approved', 'rating', 'created_at')
    search_fields = ('product__name', 'name', 'email', 'comment')
    readonly_fields = (
        'product',
        'user',
        'name',
        'email',
        'rating',
        'comment',
        'is_approved',
        'created_at',
    )
    ordering = ('-created_at',)
    actions = ['approve_reviews', 'reject_reviews']

    def rating_stars(self, obj):
        stars = '★' * obj.rating + '☆' * (5 - obj.rating)
        return format_html('<span style="color:#f59e0b; font-weight:700;">{}</span>', stars)

    rating_stars.short_description = 'امتیاز'

    def status_badge(self, obj):
        if obj.is_approved:
            return format_html(
                '<span style="background-color: rgba(22,163,74,0.12); color:#15803d; padding:4px 10px; border-radius:12px;">{}</span>',
                'تایید شده'
            )
        return format_html(
            '<span style="background-color: rgba(234,179,8,0.12); color:#b45309; padding:4px 10px; border-radius:12px;">{}</span>',
            'در انتظار تایید'
        )

    status_badge.short_description = 'وضعیت'

    
    @admin.action(description='تایید نظرات انتخاب شده')
    def approve_reviews(self, request, queryset):
         queryset.update(is_approved=True)

    @admin.action(description='رد نظرات انتخاب شده')
    def reject_reviews(self, request, queryset):
        queryset.update(is_approved=False)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser


@admin.register(ProductReviewReply)
class ProductReviewReplyAdmin(admin.ModelAdmin):
    list_display = ("review", "name", "status_badge", "created_at")
    list_filter = ("is_approved", "created_at")
    search_fields = ("review__product__name", "name", "comment")
    readonly_fields = (
        "review",
        "user",
        "name",
        "email",
        "comment",
        "is_approved",
        "created_at",
    )
    actions = ["approve_replies", "reject_replies"]
    def status_badge(self, obj):
        if obj.is_approved:
            return format_html(
                '<span style="background-color: rgba(22,163,74,0.12); color:#15803d; padding:4px 10px; border-radius:12px;">{}</span>',
                "تایید شده",
            )
        return format_html(
            '<span style="background-color: rgba(234,179,8,0.12); color:#b45309; padding:4px 10px; border-radius:12px;">{}</span>',
            "در انتظار تایید",
        )

    status_badge.short_description = "وضعیت"

    @admin.action(description="تایید پاسخ‌های انتخاب شده")
    def approve_replies(self, request, queryset):
        queryset.update(is_approved=True)

    @admin.action(description="رد پاسخ‌های انتخاب شده")
    def reject_replies(self, request, queryset):
        queryset.update(is_approved=False)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser