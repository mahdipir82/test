from django import forms
from django.forms import ModelForm
from .models import CustomUser,Customer
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import ReadOnlyPasswordHashField
import re

class UserCreationForm(forms.ModelForm):
    password1=forms.CharField(label='Password',widget=forms.PasswordInput)
    password2=forms.CharField(label='RePassword',widget=forms.PasswordInput)
    class Meta:
        model=CustomUser
        fields=['mobile_number','email','name','family']
        
    def celan_password2(self):
        pass1=self.cleaned_data['password1']
        pass2=self.cleaned_data['password2']
        if pass1 and pass2 and pass1!= pass2:
            raise ValidationError('رمز عبور و تکرار ان باهم مغایرت ندارد')
        return pass2
    
    def save(self, commit =True):
        user=super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user
#=======================================================================================    
class UserChangeForm(forms.ModelForm):
    password=ReadOnlyPasswordHashField(help_text="برای تغییر رمز عبور رو این <a href='../password'>لینک</a> کیلیک کنید")
    class Meta:
        model=CustomUser
        fields=['mobile_number','password','email','name','family','is_active','is_admin']
#=======================================================================================
from django import forms
from django.core.exceptions import ValidationError
from .models import CustomUser
import re

class RegisterUserForm(forms.ModelForm):
    password1 = forms.CharField(
        label='رمز عبور',
        widget=forms.PasswordInput(attrs={
            "class": "input-glass w-full px-4 py-3 rounded-xl focus:outline-none dark:text-white dark:placeholder-gray-400",
            "placeholder": "حداقل ۸ کاراکتر و شامل یک حرف انگلیسی باشد",
        })
    )
    password2 = forms.CharField(
        label='تکرار رمز عبور',
        widget=forms.PasswordInput(attrs={
            "class": "input-glass w-full px-4 py-3 rounded-xl focus:outline-none dark:text-white dark:placeholder-gray-400",
            "placeholder": "تکرار رمز عبور را وارد کنید",
        })
    )

    class Meta:
        model = CustomUser
        fields = ['mobile_number']
        widgets = {
            'mobile_number_register': forms.TextInput(attrs={
                'name':'mobile_number_register',
                'id':'mobile_number_register',
                'class': 'input-glass w-full px-4 py-3 rounded-xl focus:outline-none dark:text-white dark:placeholder-gray-400',
                'placeholder': '(مثال: 09123456789)',
            })
        }

    def clean_mobile_number(self):
        mobile = self.cleaned_data.get("mobile_number")
        if not re.match(r"^09\d{9}$", mobile):
            raise ValidationError("شماره موبایل وارد شده صحیح نمی‌باشد. (مثال: 09123456789)")
        if CustomUser.objects.filter(mobile_number=mobile).exists():
            raise ValidationError("این شماره موبایل قبلاً ثبت‌نام کرده است.")
        return mobile

    def clean_password1(self):
        password = self.cleaned_data.get("password1")
        if len(password) < 8:
            raise ValidationError("رمز عبور باید حداقل ۸ کاراکتر باشد.")
        if not re.search(r"[a-zA-Z]", password):
            raise ValidationError("رمز عبور باید حداقل شامل یک حرف انگلیسی باشد.")
        return password

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get("password1") != cleaned_data.get("password2"):
            raise ValidationError({"password2": "رمز عبور و تکرار آن با هم مغایرت دارد."})
        return cleaned_data


#==========================================================================================
class VerifyRegisterForm(forms.Form):
    active_code=forms.CharField(label='کد فعال سازی'
                                 ,error_messages={"required":"این فیلد نمیتواند خالی باشد"},
                                 widget=forms.TextInput(attrs={'class':"input-glass w-full px-4 py-3 rounded-xl focus:outline-none dark:text-white dark:placeholder-gray-400","id": "id_active_code",
                                      'placeholder':'  کد دریافتی را وارد کنید'}))
#==========================================================================================
class LoginUserForm(forms.Form):
    mobile_number=forms.CharField(label='شماره موبایل '
                                 ,error_messages={"required":"این فیلد نمیتواند خالی باشد",},
                                 widget=forms.TextInput(attrs={'class':"input-glass w-full px-4 py-3 rounded-xl focus:outline-none dark:text-white dark:placeholder-gray-400",
                                      'placeholder':'  موبایل را وارد کنید'}))
    password=forms.CharField(label='رمز عبور'
                                 ,error_messages={"required":"این فیلد نمیتواند خالی باشد"},
                                 widget=forms.PasswordInput(attrs={'class':"input-glass w-full px-4 py-3 rounded-xl focus:outline-none dark:text-white dark:placeholder-gray-400",
                                      'placeholder':'  رمز عبور را وارد کنید'}))
    def clean_mobile_number(self):
        mobile = self.cleaned_data.get("mobile_number")
        if not re.match(r"^09\d{9}$", mobile):
            raise forms.ValidationError("شماره موبایل وارد شده صحیح نمی‌باشد. (مثال: 09123456789)")

        return mobile
#==========================================================================================
class ChangePasswordForm(forms.Form):
    password1=forms.CharField(label='رمز عبور'
                                 ,error_messages={"required":"این فیلد نمیتواند خالی باشد"},
                                 widget=forms.PasswordInput(attrs={'class':"input-glass w-full px-4 py-3 rounded-xl focus:outline-none dark:text-white dark:placeholder-gray-400",
                                      'placeholder':'  رمز عبور را وارد کنید'}))
    password2=forms.CharField(label='تکرار رمز عبور'
                                 ,error_messages={"required":"این فیلد نمیتواند خالی باشد"},
                                 widget=forms.PasswordInput(attrs={'class':"input-glass w-full px-4 py-3 rounded-xl focus:outline-none dark:text-white dark:placeholder-gray-400",
                                      'placeholder':'  تکرار رمز عبور را وارد کنید'}))
    def celan_password2(self):
        pass1=self.cleaned_data['password1']
        pass2=self.cleaned_data['password2']
        if pass1 and pass2 and pass1!= pass2:
            raise ValidationError('رمز عبور و تکرار ان باهم مغایرت ندارد')
        return pass2
#==========================================================================================
class RememberPasswordForm(forms.Form):
    mobile_number = forms.CharField(
        label='شماره موبایل',
        error_messages={"required": "این فیلد نمی‌تواند خالی باشد"},
        widget=forms.TextInput(attrs={'class':"input-glass w-full px-4 py-3 rounded-xl focus:outline-none dark:text-white dark:placeholder-gray-400", 'placeholder':'شماره موبایل را وارد کنید'})
    )

    def clean_mobile_number(self):
        mobile = self.cleaned_data.get("mobile_number")
        if not re.match(r"^09\d{9}$", mobile):
            raise forms.ValidationError("شماره موبایل وارد شده صحیح نمی‌باشد. (مثال: 09123456789)")
        return mobile
#==========================================================================================
import os
from django import forms
from django.conf import settings
from .models import CustomUser

class ProfileUpdateForm(forms.ModelForm):
    name = forms.CharField(
        label="نام",
        required=True,
        widget=forms.TextInput(attrs={"class": "input-glass w-full px-4 py-3 rounded-xl focus:outline-none dark:text-white dark:placeholder-gray-400", "placeholder": "نام خود را وارد کنید"})
    )
    family = forms.CharField(
        label="نام خانوادگی",
        required=True,
        widget=forms.TextInput(attrs={"class": "form-input", "placeholder": "نام خانوادگی خود را وارد کنید"})
    )
    email = forms.EmailField(
        label="ایمیل",
        required=True,
        widget=forms.EmailInput(attrs={"class": "form-input", "placeholder": "ایمیل خود را وارد کنید"})
    )
    mobile_number = forms.CharField(
        label="شماره موبایل",
        required=False,
        disabled=True,  # فقط نمایش، نه ویرایش
        widget=forms.TextInput(attrs={"class": "form-input", "readonly": "readonly"})
    )

    class Meta:
        model = Customer
        fields = [
            'national_code',
            'birth_date',
            'refund_method',
        ]
        widgets = {
            'national_code': forms.TextInput(attrs={"class": "form-input", "placeholder": "کد ملی"}),
            'birth_date': forms.DateInput(attrs={"type": "date", "class": "form-input"}),
            'refund_method': forms.TextInput(attrs={"class": "form-input", "placeholder": "روش بازگرداندن پول"}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if self.user:
            self.fields['name'].initial = self.user.name
            self.fields['family'].initial = self.user.family
            self.fields['email'].initial = self.user.email
            self.fields['mobile_number'].initial = self.user.mobile_number

    def save(self, commit=True):
        CustomUser = super().save(commit=False)

        if self.user:
            self.user.name = self.cleaned_data['name']
            self.user.family = self.cleaned_data['family']
            self.user.email = self.cleaned_data['email']

            if commit:
                self.user.save()
                CustomUser.user = self.user
                CustomUser.phone_number = self.user.mobile_number


                CustomUser.save()

        return CustomUser

