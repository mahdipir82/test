from django.urls import path

from .views import FinalizeOrderAPIView

app_name = "orders"

urlpatterns = [
    path("api/finalize/", FinalizeOrderAPIView.as_view(), name="finalize"),
]