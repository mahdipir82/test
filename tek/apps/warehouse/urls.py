from django.urls import path
from .views import StockListAPIView, StockMovementAPIView

app_name = 'warehouse'

urlpatterns = [
    path('stocks/', StockListAPIView.as_view(), name='stock-list'),
    path('movements/', StockMovementAPIView.as_view(), name='stock-movement'),
]
