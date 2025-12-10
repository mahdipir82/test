from rest_framework.routers import DefaultRouter
from apps.products.views import BrandViewSet, CategoryViewSet, ProductViewSet
from .views import ProductListAPIView
from django.urls import path
from . import views
app_name="products"
router = DefaultRouter()
router.register('brands', BrandViewSet)
router.register('categories', CategoryViewSet)
router.register('products', ProductViewSet)

urlpatterns = [
    path("api/list/", ProductListAPIView.as_view(), name="product_list"),
    path('laptops/', views.laptops_page, name='laptops_page'),
    path('computers/', views.computers_page, name='computers_page'),
    path('accessories/', views.accessories_page, name='accessories_page'),
    path('<slug:slug>/', views.product_detail, name='product_detail'),
] + router.urls
