from django import forms
from .models import BlogComment


class BlogCommentForm(forms.ModelForm):
    class Meta:
        model = BlogComment
        fields = ['name', 'email', 'rating', 'content']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'input-glass', 'placeholder': 'نام شما'}),
            'email': forms.EmailInput(attrs={'class': 'input-glass', 'placeholder': 'ایمیل'}),
            'rating': forms.Select(attrs={'class': 'input-glass'}),
            'content': forms.Textarea(attrs={'class': 'input-glass', 'rows': 4, 'placeholder': 'نظر شما'}),
        }
        labels = {
            'name': 'نام',
            'email': 'ایمیل',
            'rating': 'امتیاز',
            'content': 'متن نظر',
        }