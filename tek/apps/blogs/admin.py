from django.contrib import admin

from .models import BlogComment, BlogPost


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_published', 'created_at', 'average_rating')
    list_filter = ('is_published', 'created_at')
    search_fields = ('title', 'content')
    prepopulated_fields = {'slug': ('title',)}


@admin.register(BlogComment)
class BlogCommentAdmin(admin.ModelAdmin):
    list_display = ('name', 'post', 'rating', 'is_approved', 'created_at')
    list_filter = ('is_approved', 'rating', 'created_at')
    search_fields = ('name', 'email', 'content')
    actions = ['approve_comments']

    @admin.action(description='تایید نظرات انتخاب شده')
    def approve_comments(self, request, queryset):
        queryset.update(is_approved=True)