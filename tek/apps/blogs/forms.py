from django import forms
from .models import BlogComment

class BlogCommentForm(forms.ModelForm):
    class Meta:
        model = BlogComment
        fields = ['name', 'email', 'rating', 'content']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'input', 'placeholder': 'نام شما'}),
            'email': forms.EmailInput(attrs={'class': 'input', 'placeholder': 'ایمیل'}),
            'rating': forms.Select(attrs={'class': 'input'}),
            'content': forms.Textarea(attrs={'class': 'input', 'rows': 4, 'placeholder': 'نظر شما'}),
        }
