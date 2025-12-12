from django.db.models import Sum
from apps.products.models import Product


def fetch_products():
    try:
        products = (
            Product.objects.filter(is_active=True)
            .annotate(stock_quantity=Sum("stocks__quantity"))
            .prefetch_related("categories")
        )
        data = []
        for product in products:
            categories = [category.title for category in product.categories.all()]
            data.append(
                {
                    "id": product.id,
                    "name": product.name,
                    "categories": categories,
                    "stock_quantity": product.stock_quantity or product.stock,
                    "originalPrice": product.price,
                    "finalPrice": product.get_price_after_discount(),
                }
            )
        return data
    except Exception:
        return []
