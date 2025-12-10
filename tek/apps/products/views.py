from django.db.models import Avg
from django.shortcuts import get_object_or_404, redirect, render
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from .forms import ProductReviewForm
from .models import Brand, Category, Product
from .serializers import BrandSerializer, CategorySerializer, ProductSerializer


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
def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    approved_reviews = product.approved_reviews.order_by('-created_at')
    average_rating = approved_reviews.aggregate(avg=Avg('rating')).get('avg') or 0

    if request.method == 'POST':
        form = ProductReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            if request.user.is_authenticated:
                review.user = request.user
            review.save()
            return redirect('products:product_detail', slug=product.slug)
    else:
        initial = {}
        if request.user.is_authenticated:
            initial = {
                'name': request.user.get_full_name() or request.user.username,
                'email': request.user.email,
            }
        form = ProductReviewForm(initial=initial)

    return render(
        request,
        "products_app/product_detail.html",
        {
            "product": product,
            "reviews": approved_reviews,
            "average_rating": round(average_rating, 1) if average_rating else 0,
            "form": form,
        },
    )



