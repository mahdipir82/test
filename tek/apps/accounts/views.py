from django.shortcuts import render,redirect
from django.utils.decorators import method_decorator
from django.views import View
from .forms import RegisterUserForm,VerifyRegisterForm,LoginUserForm,ChangePasswordForm,RememberPasswordForm,ProfileUpdateForm
import utils
from django.utils import timezone
from django.views.generic import TemplateView
from rest_framework.permissions import IsAuthenticated
from .models import CustomUser,Customer, Address
import json
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from django.conf import settings
from django.http import JsonResponse
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .serializers import MyTokenObtainPairSerializer
import time
#===============================================================
class ResendCodeView(View):
    def post(self, request):
        # بررسی نشست کاربر
        user_session = request.session.get("user_session")
        if not user_session:
            return JsonResponse({"status": "error", "message": "نشست کاربر یافت نشد"}, status=400)

        mobile = user_session.get("mobile_number")
        try:
            user = CustomUser.objects.get(mobile_number=mobile)
        except CustomUser.DoesNotExist:
            return JsonResponse({"status": "error", "message": "کاربر یافت نشد"}, status=404)

        # بررسی زمان ارسال کد فعال‌سازی
        cooldown = getattr(settings, "VERIFICATION_RESEND_COOLDOWN", 120)
        now = timezone.now()
        if user.last_code_sent:
            diff = (now - user.last_code_sent).total_seconds()
            if diff < cooldown:
                return JsonResponse({
                    "status": "cooldown",
                    "remaining": int(cooldown - diff),
                    "message": f"لطفا {int(cooldown - diff)} ثانیه صبر کنید."
                }, status=429)

        # ایجاد کد جدید
        code = utils.create_random_code(5)
        user.active_code = code  # کد فعال سازی جدید
        user.last_code_sent = now

        # ارسال کد جدید به شماره موبایل
        utils.send_sms(mobile, f"کد فعال سازی شما {code} می‌باشد")

        # ذخیره کد در نشست برای استفاده در تایید کد
        user_session['active_code'] = str(code)
        request.session['user_session'] = user_session
        request.session.modified = True

        # در اینجا `is_active` تغییر نمی‌کند چون منتظر تایید کد هستیم
        user.save()

        return JsonResponse({"status": "sent", "message": "کد فعال سازی مجدداً ارسال شد", "cooldown": cooldown})

#===============================================================
from django.views import View
from django.shortcuts import render, redirect
from django.http import JsonResponse
from .forms import RegisterUserForm
from .models import CustomUser
from utils import create_random_code
import json
class RegisterUserView(View):
    template_name = "accounts_app/register.html"

    def get(self, request, *args, **kwargs):
        form = RegisterUserForm()
        return render(request, self.template_name, {"form": form})

    def post(self, request, *args, **kwargs):
        # اگر از فرم HTML اومده:
        if request.content_type == "application/x-www-form-urlencoded":
            form = RegisterUserForm(request.POST)
        else:
            # اگر از fetch یا axios اومده (JSON)
            import json
            try:
                data = json.loads(request.body)
            except json.JSONDecodeError:
                return JsonResponse({"success": False, "message": "JSON نامعتبر"}, status=400)
            form = RegisterUserForm(data)

        if not form.is_valid():
            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return JsonResponse({"success": False, "errors": form.errors}, status=400)
            return render(request, self.template_name, {"form": form})

        mobile = form.cleaned_data["mobile_number"]
        password = form.cleaned_data["password1"]

        user, created = CustomUser.objects.get_or_create(
            mobile_number=mobile, defaults={"is_active": False}
        )
        if not created and user.is_active:
            msg = "شما قبلاً ثبت‌نام کرده‌اید."
            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return JsonResponse({"success": False, "message": msg}, status=400)
            return render(request, self.template_name, {"form": form, "error": msg})

        code = utils.create_random_code(5)
        user.active_code = code
        user.set_password(password)
        
        user.save()
        utils.send_sms(mobile, f"کد فعال‌سازی شما: {code}")

        request.session["user_session"] = {
            "mobile_number": mobile,
            "active_code": str(code),
            "remember_password": False,
        }

        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"success": True, "redirect": "/accounts/verify/"})
        return redirect("accounts:verify")


   
#=====================================================================


#==============================================================================================

class LoginUserView(View):
    template_name = "accounts_app/login.html"

    def get(self, request):
        form = LoginUserForm()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        is_json = request.content_type.startswith("application/json")

        if is_json:
            data = json.loads(request.body)
            mobile = data.get("mobile_number")
            password = data.get("password")
        else:
            form = LoginUserForm(request.POST)
            if not form.is_valid():
                return render(request, self.template_name, {"form": form, "error": "اطلاعات نامعتبر"})
            mobile = form.cleaned_data["mobile_number"]
            password = form.cleaned_data["password"]

        user = authenticate(request, username=mobile, password=password)
        if not user:
            msg = "شماره موبایل یا رمز اشتباه است."
            if is_json:
                return JsonResponse({"success": False, "message": msg}, status=401)
            return render(request, self.template_name, {"form": LoginUserForm(), "error": msg})

        login(request, user)

        refresh = RefreshToken.for_user(user)
        access = str(refresh.access_token)

        # در حالت JSON:
        if is_json:
            return JsonResponse({
                "success": True,
                "message": "ورود موفقیت‌آمیز!",
                "access": access,
                "refresh": str(refresh),
                "redirect": "/"
            })

        # در حالت HTML هم JSON می‌ده تا جاوااسکریپت ذخیره کنه:
        return JsonResponse({
            "success": True,
            "message": "ورود موفقیت‌آمیز!",
            "access": access,
            "refresh": str(refresh),
            "redirect": "/"
        })

#=======================================================================================
class LogoutUserView(View):
    def get(self, request, *args, **kwargs):
        session_cart = request.session.get("shop_cart", {})
        logout(request)
        request.session["shop_cart"] = session_cart
        return redirect("main:index")
#=======================================================================================
class ChangePasswordView(View):
    template_name = "accounts_app/change_password.html"

    def get(self, request):
        # فقط کاربرانی که session user_session دارند
        if not request.session.get("user_session"):
            return redirect("/accounts/remember_password/")

        form = ChangePasswordForm()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        # بررسی اینکه درخواست از نوع JSON باشد یا فرم معمولی
        is_json = request.content_type == "application/json"
        try:
            # در صورتی که درخواست JSON باشد، داده‌ها از body استخراج می‌شود
            data = json.loads(request.body) if is_json else request.POST
        except json.JSONDecodeError:
            return JsonResponse({"success": False, "message": "فرمت JSON نامعتبر"}, status=400)

        form = ChangePasswordForm(data)
        if not form.is_valid():
            # اگر فرم معتبر نباشد، پیام خطا نمایش داده می‌شود
            if is_json:
                return JsonResponse({"success": False, "message": "اطلاعات وارد شده معتبر نیست"})
            return render(request, self.template_name, {"form": form})

        # گرفتن اطلاعات session
        user_session = request.session.get("user_session")
        if not user_session:
            return JsonResponse({"success": False, "message": "نشست کاربر منقضی شده است"}, status=400)

        try:
            # یافتن کاربر بر اساس شماره موبایل موجود در session
            user = CustomUser.objects.get(mobile_number=user_session["mobile_number"])
        except CustomUser.DoesNotExist:
            return JsonResponse({"success": False, "message": "کاربر یافت نشد"}, status=404)

        # گرفتن کلمه عبور جدید
        password1 = form.cleaned_data.get("password1")
        # تنظیم رمز عبور جدید
        user.set_password(password1)
        user.save()

        # پاک کردن session
        del request.session["user_session"]

        # اگر درخواست از نوع JSON باشد، پیامی برای موفقیت به کاربر ارسال می‌کنیم
        if is_json:
            return JsonResponse({"success": True, "message": "رمز شما با موفقیت تغییر کرد", "redirect": "/accounts/login/"})
        else:
            # اگر درخواست از نوع فرم باشد، کاربر به صفحه ورود هدایت می‌شود
            return redirect("/accounts/login/")


#=======================================================================================
class RememberPasswordView(View):
    template_name = 'accounts_app/remember_password.html'

    def get(self, request):
        form = RememberPasswordForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        # بررسی JSON یا فرم
        is_json = request.content_type == "application/json"
        if is_json:
            try:
                data = json.loads(request.body)
            except json.JSONDecodeError:
                return JsonResponse({"success": False, "message": "فرمت JSON نامعتبر"}, status=400)
        else:
            data = request.POST

        form = RememberPasswordForm(data)
        if not form.is_valid():
            message = "شماره موبایل نامعتبر"
            if is_json:
                return JsonResponse({"success": False, "message": message})
            return render(request, self.template_name, {"form": form, "error": message})

        mobile = form.cleaned_data['mobile_number']
        try:
            user = CustomUser.objects.get(mobile_number=mobile)
        except CustomUser.DoesNotExist:
            message = "شماره موبایل موجود نیست"
            if is_json:
                return JsonResponse({"success": False, "message": message})
            return render(request, self.template_name, {"form": form, "error": message})

        # تولید کد و ذخیره در DB و سشن
        code = utils.create_random_code(5)
        user.active_code = code
        user.save()
        utils.send_sms(mobile, f"کد تایید شماره موبایل شما: {code}")

        request.session['user_session'] = {
            'active_code': str(code),
            'mobile_number': mobile,
            'remember_password': True
        }
        request.session.modified = True

        response = {"success": True, "message": "کد فعال‌سازی به شماره موبایل شما ارسال شد", "redirect": "/accounts/verify/"}
        if is_json:
            return JsonResponse(response)
        return redirect("/accounts/verify/")
#==============================================================================================
class VerifyRegisterCodeView(View):
    def post(self, request):
        # تشخیص JSON یا فرم
        is_json = request.content_type == "application/json"
        try:
            data = json.loads(request.body) if is_json else request.POST
        except json.JSONDecodeError:
            return JsonResponse({"success": False, "message": "فرمت JSON نامعتبر"}, status=400)

        form = VerifyRegisterForm(data)
        if not form.is_valid():
            return JsonResponse({"success": False, "message": "کد فعال‌سازی نامعتبر"}, status=400)

        user_session = request.session.get("user_session")
        if not user_session:
            return JsonResponse({"success": False, "message": "دسترسی غیرمجاز. لطفاً دوباره تلاش کنید"}, status=401)

        active_code = str(form.cleaned_data.get("active_code"))
        if active_code != str(user_session.get("active_code")):
            return JsonResponse({"success": False, "message": "کد فعال‌سازی اشتباه است"}, status=400)

        # پیدا کردن کاربر
        try:
            user = CustomUser.objects.get(mobile_number=user_session["mobile_number"])
        except CustomUser.DoesNotExist:
            return JsonResponse({"success": False, "message": "کاربر یافت نشد"}, status=404)

        # رفتار براساس اینکه فراموشی رمز بوده یا ثبت‌نام
        if user_session.get("remember_password"):
            # فراموشی رمز → اجازه تغییر رمز (بعدا به change_password می‌رویم)
            # توجه: ممکن است نخواهی user.is_active را تغییر دهی؛ من فعلاً فعال می‌کنم
            user.is_active = True
            user.save()

            # نگه داشتن سشن برای change password
            request.session["user_session"] = {
                "mobile_number": user.mobile_number,
                "remember_password": True,
                "verified": True
            }
            request.session.modified = True

            return JsonResponse({
                "success": True,
                "message": "کد تایید شد. اکنون می‌توانید رمز خود را تغییر دهید.",
                "redirect": "/accounts/change_password/",
                "after": "remember"
            })

        else:
            # ثبت‌نام → فعال‌سازی و هدایت به صفحه ورود (یا login modal)
            user.is_active = True
            user.save()
            login(request, user)  # اگر می‌خواهی کاربر را لاگین کنی

            request.session["user_session"] = {
                "mobile_number": user.mobile_number,
                "remember_password": False,
                "verified": True
            }
            request.session.modified = True

            return JsonResponse({
                "success": True,
                "message": "ثبت‌نام با موفقیت انجام شد.",
                "redirect": "/accounts/login/",
                "after": "register"
            })










class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

class LogoutAndBlacklistRefreshTokenView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception:
            return Response(status=status.HTTP_400_BAD_REQUEST)

class CurrentUserView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user = request.user
        data = {
            'id': user.id,
            'mobile_number': user.mobile_number,
            'name': user.name,
            'family': user.family,
            'email': user.email,
        }
        return Response(data)
#=================================================
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
from django.http import JsonResponse
from django.contrib.auth import update_session_auth_hash
import json
from django.contrib import messages
# صفحه پروفایل
class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = "accounts_app/profile.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        customer, _ = Customer.objects.get_or_create(user=user)
        context["user_data"] = user
        context["customer_data"] = customer
        context["user_addresses"] = Address.objects.filter(customer=user)

        session_cart = self.request.session.get("shop_cart", {})
        cart_items = session_cart.values() if isinstance(session_cart, dict) else session_cart
        context["profile_cart_items"] = cart_items
        context["profile_cart_json"] = json.dumps(list(cart_items), ensure_ascii=False)
        return context


# API برای گرفتن اطلاعات پروفایل
class ProfileAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        customer, _ = Customer.objects.get_or_create(user=user)

        return Response({
            "name": user.name,
            "family": user.family,
            "email": user.email,
            "mobile_number": user.mobile_number,
            "national_code": customer.national_code,
            "birth_date": customer.birth_date,
        })

@method_decorator(login_required, name='dispatch')
class UpdateProfileAPI(View):
    def post(self, request):
        data = request.POST
        user = request.user
        customer, _ = Customer.objects.get_or_create(user=user)

        # --- UPDATE USER ---
        if data.get("name"):
            user.name = data.get("name")
        if data.get("family"):
            user.family = data.get("family")
        if data.get("email"):
            user.email = data.get("email")
        user.save()

        # --- UPDATE CUSTOMER ---
        if data.get("national_code"):
            customer.national_code = data.get("national_code")
        if data.get("birth_date"):
            customer.birth_date = data.get("birth_date")
        customer.save()

        return JsonResponse({
            "success": True,
            "message": "پروفایل با موفقیت ذخیره شد",
            "user": {
                "name": user.name,
                "family": user.family,
                "email": user.email,
                "mobile_number": user.mobile_number,
                "national_code": customer.national_code,
                "birth_date": customer.birth_date,
            }
        })
        
        

# views.py
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Address

@login_required
def get_addresses(request):
    user = request.user  # گرفتن کاربر وارد شده
    addresses = Address.objects.filter(customer=user)  # گرفتن آدرس‌ها برای کاربر
    address_list = []

    for address in addresses:
        address_list.append({
            'title': address.title,
            'province': address.province,
            'city': address.city,
            'full_address': address.full_address,
            'postal_code': address.postal_code,
        })

    return JsonResponse({'addresses': address_list})


@login_required
def add_address(request):
    if request.method == 'POST':
        data = json.loads(request.body)  # داده‌های ارسال شده از سمت فرانت‌اند
        title = data.get('title')
        province = data.get('province')
        city = data.get('city')
        full_address = data.get('full_address')
        postal_code = data.get('postal_code')

        user = request.user
        new_address = Address.objects.create(
            customer=user,
            title=title,
            province=province,
            city=city,
            full_address=full_address,
            postal_code=postal_code
        )

        # دریافت آدرس‌های جدید و ارسال آن‌ها به کلاینت
        addresses = Address.objects.filter(customer=user)
        address_list = []

        for address in addresses:
            address_list.append({
                'title': address.title,
                'province': address.province,
                'city': address.city,
                'full_address': address.full_address,
                'postal_code': address.postal_code,
            })

        return JsonResponse({'success': True, 'message': 'آدرس با موفقیت اضافه شد!', 'addresses': address_list})
