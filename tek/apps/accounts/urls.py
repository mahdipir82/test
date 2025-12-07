from  django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenRefreshView
from .views import MyTokenObtainPairView, LogoutAndBlacklistRefreshTokenView, CurrentUserView
from .views import ProfileView,ProfileAPI,UpdateProfileAPI
app_name="accounts"
urlpatterns=[

    path('register/', views.RegisterUserView.as_view(), name="register"),
    path('verify/', views.VerifyRegisterCodeView.as_view(), name="verify"),
    path('login/', views.LoginUserView.as_view(), name="login"),
    path('logout/', views.LogoutUserView.as_view(), name="logout"),
    path('change_password/', views.ChangePasswordView.as_view(), name="change_password"),
    path('remember_password/', views.RememberPasswordView.as_view(), name='remember_password'),
    path('resend-code/', views.ResendCodeView.as_view(), name="resend_code"),
    
    # ✅ فعال کردن JWT
    path('api/token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/logout/', LogoutAndBlacklistRefreshTokenView.as_view(), name='token_logout'),
    path('api/me/', CurrentUserView.as_view(), name='api_me'),
    
   
   
   #user
    path('profile/', ProfileView.as_view(), name='profile'),
    path('profile/api/', ProfileAPI.as_view(), name='profile_api'),
    path('profile/update/api/', UpdateProfileAPI.as_view(), name='update_profile_api'),
    path('add_address/', views.add_address, name='add_address'),
    path('get_addresses/', views.get_addresses, name='get_addresses'),
    # path('edit_profile/', EditProfileView.as_view(), name='edit_profile'),

    ]
    

