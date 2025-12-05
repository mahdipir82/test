from django.urls import path
from .views import ApplyDiscountAPIView

app_name = "discounts"

urlpatterns = [
    path("apply/", ApplyDiscountAPIView.as_view(), name="apply_discount"),
]
