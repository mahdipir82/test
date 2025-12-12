from django.shortcuts import render

from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView


from apps.products.models import Product
from apps.warehouse.models import Stock, StockMovement, Warehouse


@method_decorator(csrf_exempt, name="dispatch")
class FinalizeOrderAPIView(APIView):
    permission_classes = [AllowAny]

    def _get_default_warehouse(self, warehouse_id=None):
        if warehouse_id:
            warehouse = Warehouse.objects.filter(id=warehouse_id).first()
            if warehouse:
                return warehouse
        warehouse, _ = Warehouse.objects.get_or_create(name="انبار اصلی")
        return warehouse

    def post(self, request):
        items = request.data.get("items", [])
        warehouse_id = request.data.get("warehouse_id")

        if not isinstance(items, list) or not items:
            return Response({"error": "آیتمی برای ثبت سفارش ارسال نشده است."}, status=400)

        warehouse = self._get_default_warehouse(warehouse_id)
        updated_items = []

        with transaction.atomic():
            for item in items:
                product_id = item.get("product_id")
                quantity = int(item.get("quantity", 0))
                if not product_id or quantity <= 0:
                    continue

                product = get_object_or_404(Product, id=product_id)
                product.stock = max(product.stock - quantity, 0)
                product.save(update_fields=["stock"])

                movement = StockMovement.objects.create(
                    product=product,
                    warehouse=warehouse,
                    movement_type=StockMovement.OUT,
                    quantity=quantity,
                    description="کاهش موجودی پس از ثبت سفارش",
                )

                stock_record = Stock.objects.get(product=product, warehouse=warehouse)
                updated_items.append(
                    {
                        "product": product.name,
                        "ordered_quantity": quantity,
                        "remaining_product_stock": product.stock,
                        "warehouse_stock": stock_record.quantity,
                        "movement_id": movement.id,
                    }
                )

        return Response(
            {
                "message": "سفارش ثبت شد و موجودی به‌روز شد.",
                "warehouse": warehouse.name,
                "items": updated_items,
            }
        )
