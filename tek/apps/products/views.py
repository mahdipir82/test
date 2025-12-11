from django.db.models import Avg
from django.shortcuts import get_object_or_404, redirect, render
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from .serializers import ProductReviewSerializer, ProductReviewCreateSerializer
from .forms import ProductReviewForm
from .models import Brand, Category, Product, ProductReview
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
        serializer = ProductSerializer(products, many=True, context={"request": request})
        return Response(serializer.data)
    
@method_decorator(csrf_exempt, name="dispatch")
class ProductReviewAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, slug):
        product = get_object_or_404(Product, slug=slug, is_active=True)
        reviews = product.approved_reviews.order_by("-created_at")
        serializer = ProductReviewSerializer(reviews, many=True)
        return JsonResponse(
            {
                "reviews": serializer.data,
                "average_rating": product.average_rating,
                "review_count": reviews.count(),
            }
        )

    def post(self, request, slug):
        product = get_object_or_404(Product, slug=slug, is_active=True)
        data = request.POST or request.data if hasattr(request, "data") else {}
        serializer = ProductReviewCreateSerializer(data=data)
        if serializer.is_valid():
            ProductReview.objects.create(
                product=product,
                name=serializer.validated_data["name"],
                email=serializer.validated_data.get("email"),
                rating=serializer.validated_data["rating"],
                comment=serializer.validated_data["comment"],
                user=request.user if request.user.is_authenticated else None,
            )
            return JsonResponse(
                {
                    "message": "نظر شما ثبت شد و پس از تایید نمایش داده می‌شود.",
                    "average_rating": product.average_rating,
                    "review_count": product.approved_reviews.count(),
                },
                status=201,
            )

        return JsonResponse(serializer.errors, status=400)
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



