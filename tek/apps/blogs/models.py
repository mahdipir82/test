from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from utils import FileUpload


class BlogPost(models.Model):
    title = models.CharField(max_length=200, verbose_name='عنوان')
    slug = models.SlugField(max_length=220, unique=True, verbose_name='اسلاگ')
    content = models.TextField(verbose_name='محتوا')
    cover_upload = FileUpload('images', 'blogs')
    cover_image = models.ImageField(
        upload_to=cover_upload.upload_to,
        null=True,
        blank=True,
        verbose_name='تصویر شاخص',
    )
    is_published = models.BooleanField(default=True, verbose_name='منتشر شده')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاریخ بروزرسانی')

    class Meta:
        verbose_name = 'مقاله'
        verbose_name_plural = 'مقالات'
        ordering = ('-created_at',)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('blogs:post_detail', kwargs={'slug': self.slug})

    @property
    def average_rating(self):
        approved = self.comments.filter(is_approved=True)
        if not approved.exists():
            return 0
        return round(approved.aggregate(models.Avg('rating'))['rating__avg'] or 0, 1)


class BlogComment(models.Model):
    RATING_CHOICES = [(i, str(i)) for i in range(1, 6)]

    post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name='comments', verbose_name='مقاله')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='blog_comments',
        verbose_name='کاربر',
    )
    name = models.CharField(max_length=120, verbose_name='نام')
    email = models.EmailField(verbose_name='ایمیل')
    rating = models.PositiveSmallIntegerField(choices=RATING_CHOICES, verbose_name='امتیاز')
    content = models.TextField(verbose_name='متن نظر')
    is_approved = models.BooleanField(default=False, verbose_name='تایید شده توسط ادمین')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ارسال')

    class Meta:
        verbose_name = 'نظر مقاله'
        verbose_name_plural = 'نظرات مقالات'
        ordering = ('-created_at',)

    def __str__(self):
        return f"{self.name} - {self.post.title}"

    @property
    def display_name(self):
        if self.user and self.user.get_full_name():
            return self.user.get_full_name()
        if self.user:
            return self.user.username
        return self.name