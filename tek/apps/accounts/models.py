from django.db import models
from django.contrib.auth.models import AbstractBaseUser,PermissionsMixin,BaseUserManager
from django.utils import timezone
import email
from utils import FileUpload
from django.utils import timezone
class CustomUserManager(BaseUserManager):
    def create_user(self,mobile_number,email="",name="",family="",active_code=None,password=None):
        if not mobile_number:
            raise ValueError("شماره موبایل باید وارد شود")
        
        user=self.model(
            mobile_number=mobile_number,
            email=self.normalize_email(email),
            name=name,
            family=family,
            
            active_code=active_code,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user
    #=========================================
    def create_superuser(self,mobile_number,email,name,family,password=None,active_code=None):
        user=self.create_user(
            mobile_number=mobile_number,
            email=email,
            name=name,
            family=family,
            active_code=active_code,
            
            password=password, 
        )
        user.is_active=True
        user.is_admin=True
        user.is_superuser=True
        user.save(using=self._db)
        return user
#====================================================================
class CustomUser(AbstractBaseUser, PermissionsMixin):
    mobile_number = models.CharField(max_length=11, unique=True, verbose_name="شماره موبایل")
    email = models.EmailField(max_length=200, blank=True)
    name = models.CharField(max_length=50, blank=True)
    family = models.CharField(max_length=50, blank=True)
    is_active = models.BooleanField(default=False)
    active_code = models.CharField(max_length=100, null=True, blank=True)
    is_admin = models.BooleanField(default=False)
    last_code_sent = models.DateTimeField(null=True, blank=True)

    USERNAME_FIELD = 'mobile_number'
    REQUIRED_FIELDS = ['email', 'name', 'family']

    objects = CustomUserManager()

    def __str__(self):
        return f"{self.name} {self.family}"

    @property
    def is_staff(self):
        return self.is_admin


# ✅ اینجا Customer رو جدا تعریف کن
class Customer(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, primary_key=True)
    phone_number = models.CharField(max_length=11, null=True, blank=True)
    national_code = models.CharField(max_length=10, blank=True, null=True, verbose_name="کد ملی")
    birth_date = models.DateField(blank=True, null=True, verbose_name="تاریخ تولد")
    refund_method = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="روش بازگرداندن پول",
        help_text="مثلاً شماره شبا، کیف پول، یا کارت بانکی"
    )

    def __str__(self):
        return f"{self.user.name} {self.user.family}"
    
    
#====================================================


class Address(models.Model):
    customer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="addresses")
    title = models.CharField(max_length=255)
    province = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    full_address = models.TextField()
    postal_code = models.CharField(max_length=10)

    def __str__(self):
        return f"{self.title} - {self.city}, {self.province}"