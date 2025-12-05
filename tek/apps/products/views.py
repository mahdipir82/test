from rest_framework import viewsets
from apps.products.models import Brand, Category, Product
from apps.products.serializers import BrandSerializer, CategorySerializer, ProductSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Product
from .serializers import ProductSerializer


class BrandViewSet(viewsets.ModelViewSet):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    lookup_field = 'slug'


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'slug'


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.filter(is_active=True)
    serializer_class = ProductSerializer
    lookup_field = 'slug'


class ProductListAPIView(APIView):
    def get(self, request):
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)
    

from .models import Product, Category

from django.shortcuts import render

def laptops_page(request):
    products = Product.objects.filter(
        categories__slug="lt",
        is_active=True
    ).distinct()

    return render(request, "products_app/laptops.html", {"products": products})

def computers_page(request):
    products = Product.objects.filter(
        categories__slug="pc",
        is_active=True
    ).distinct()

    return render(request, "products_app/computers.html", {"products": products})

def accessories_page(request):
    products = Product.objects.filter(
        categories__slug="accessories",
        is_active=True
    ).distinct()

    return render(request, "products_app/accessories.html", {"products": products})


