from django import forms

from .models import ProductReview


class ProductReviewForm(forms.ModelForm):
    class Meta:
        model = ProductReview
        fields = ['name', 'email', 'rating', 'comment']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'input-glass', 'placeholder': 'نام شما'}),
            'email': forms.EmailInput(attrs={'class': 'input-glass', 'placeholder': 'ایمیل'}),
            'rating': forms.Select(attrs={'class': 'input-glass'}),
            'comment': forms.Textarea(attrs={'class': 'input-glass', 'rows': 4, 'placeholder': 'تجربه شما از محصول'}),
        }
        labels = {
            'name': 'نام',
            'email': 'ایمیل',
            'rating': 'امتیاز',
            'comment': 'متن نظر',
        }