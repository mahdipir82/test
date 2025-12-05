from rest_framework import serializers
from .models import Stock, StockMovement
from apps.products.models import Product
from .models import Warehouse

class StockSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)
    warehouse_name = serializers.CharField(source="warehouse.name", read_only=True)

    class Meta:
        model = Stock
        fields = ['id', 'product', 'product_name', 'warehouse', 'warehouse_name', 'quantity']


class StockMovementSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockMovement
        fields = ['id', 'product', 'warehouse', 'movement_type', 'quantity', 'description', 'created_at']
