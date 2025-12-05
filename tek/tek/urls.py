"""
URL configuration for tek project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static
# from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',include('apps.main.urls',namespace='main')),
    path('products/', include('apps.products.urls',namespace="products")),
    path('accounts/', include('apps.accounts.urls')),
    # path('blogs/', include('apps.blogs.urls', namespace='blogs')),
    path('api/warehouse/', include('apps.warehouse.urls', namespace='warehouse')),
    path('discounts/',include('apps.discounts.urls',namespace='discounts')),
    path("ai/", include("apps.aiassistant.urls")),
    
    # path("orders/", include("apps.orders.urls")),
    # path('ckeditor/', include('ckeditor_uploader.urls')),
    
    
]+static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)