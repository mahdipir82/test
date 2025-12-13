from django import forms
from .models import ProductReview, ProductReviewReply



class ProductReviewForm(forms.ModelForm):
    class Meta:
        model = ProductReview
        fields = ['name', 'email', 'phone_number', 'rating', 'comment']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'input-glass', 'placeholder': 'نام شما'}),
            'email': forms.EmailInput(attrs={'class': 'input-glass', 'placeholder': 'ایمیل'}),
            'phone_number': forms.TextInput(attrs={'class': 'input-glass', 'placeholder': 'شماره موبایل', 'inputmode': 'tel'}),
            'rating': forms.Select(attrs={'class': 'input-glass'}),
            'comment': forms.Textarea(attrs={'class': 'input-glass', 'rows': 4, 'placeholder': 'تجربه شما از محصول'}),
        }
        labels = {
            'name': 'نام',
            'email': 'ایمیل',
            'phone_number': 'شماره موبایل',
            'rating': 'امتیاز',
            'comment': 'متن نظر',
        
         }


class ProductReviewReplyForm(forms.ModelForm):
    class Meta:
        model = ProductReviewReply
        fields = ['name', 'email', 'comment']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'input-glass', 'placeholder': 'نام شما'}),
            'email': forms.EmailInput(attrs={'class': 'input-glass', 'placeholder': 'ایمیل'}),
            'comment': forms.Textarea(attrs={'class': 'input-glass', 'rows': 3, 'placeholder': 'پاسخ خود را بنویسید'}),
        }
        labels = {
            'name': 'نام',
            'email': 'ایمیل',
            'comment': 'پاسخ',
        
        }