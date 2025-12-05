from django.db import models

# Create your models here.
class ChatMessage(models.Model):
    ROLE_CHOICES = (
        ("user", "کاربر"),
        ("bot", "چت‌بات"),
    )

    session_id = models.CharField(max_length=100)  # می‌تونی session_id یا موبایل کاربر بذاری
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.role}: {self.message[:20]}..."