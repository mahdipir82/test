from django.contrib import admin
from .models import BlogCategory, BlogComment, BlogPost
@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'is_published', 'created_at', 'average_rating')
    list_filter = ('is_published', 'created_at', 'category')
    search_fields = ('title', 'content')
    prepopulated_fields = {'slug': ('title',)}

@admin.register(BlogCategory)
class BlogCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}
    
@admin.register(BlogComment)
class BlogCommentAdmin(admin.ModelAdmin):
    list_display = ('post', 'name', 'email', 'rating', 'is_approved', 'created_at')
    list_filter = ('is_approved', 'rating', 'created_at')
    search_fields = ('name', 'email', 'content')
    raw_id_fields = ('post', 'user')
    actions = ["approve_comments"]

    @admin.action(description="تایید نظرات انتخاب شده")
    def approve_comments(self, request, queryset):
        queryset.update(is_approved=True)