import importlib.util
import json
import uuid
from django.http import JsonResponse, StreamingHttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

if importlib.util.find_spec("openai"):
    from openai import OpenAI  # type: ignore
    client = OpenAI(api_key="YOUR_API_KEY_HERE")
else:
    OpenAI = None  # type: ignore
    client = None

from apps.main.models import SiteSetting
from .models import ChatMessage
from .utils import fetch_products

def get_store_name():
    return SiteSetting.get_store_name()

class ChatBotAPI(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        user_message = request.data.get("message")

        if not user_message:
            return Response({"error": "پیامی ارسال نشده."}, status=400)

        if client is None:
            return Response({"error": "سرویس هوش مصنوعی فعال نیست."}, status=503)

        store_name = get_store_name()

        def stream():
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                stream=True,
                messages=[
                     {
                        "role": "system",
                        "content": f"تو یک پشتیبان فروشگاه {store_name} هستی. مودب، سریع، فروشنده حرفه‌ای.",
                    },
                    {"role": "user", "content": user_message},
                ],
            )

            for chunk in response:
                if chunk.choices:
                    delta = chunk.choices[0].delta.get("content")
                    if delta:
                        yield delta


        return StreamingHttpResponse(stream(), content_type="text/plain")
    
    
    
    

class ChatBotView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        user_msg = request.data.get("message")
        store_name = get_store_name()

        if client is None:
            return Response({"error": "سرویس هوش مصنوعی فعال نیست."}, status=503)

        products = fetch_products()

        system_prompt = f"""
تو یک پشتیبان حرفه‌ای فروشگاه {store_name} هستی.

### لیست محصولات فروشگاه:
{json.dumps(products, ensure_ascii=False)}

### قوانین:
- اگر کاربر نام محصولی را گفت، در لیست جستجو کن.
- موجودی محصول = stock_quantity
- قیمت اصلی = originalPrice
- قیمت نهایی = finalPrice
- اگر موجودی صفر بود بگو موجود نیست.
- اگر چند محصول شبیه بودند، پیشنهاد بده.
- اگر کاربر بخواهد سفارش ثبت کند، فقط بپرس:
  «اسم، شماره تماس، آدرس؟»
- جواب‌ها باید کاملاً مودب، طبیعی، روان و فروشنده‌گونه باشند.
"""

        def stream():
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                stream=True,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_msg},
                ]
            )
            for chunk in response:
                if chunk.choices:
                    delta = chunk.choices[0].delta.get("content")
                    if delta:
                        yield delta
            
        return StreamingHttpResponse(stream(), content_type="text/plain")




class ChatHistoryAdminView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        messages = ChatMessage.objects.all().order_by("-created_at")[:200]   
        data = [
            {
                "session_id": m.session_id,
                "role": m.role,
                "message": m.message,
                
                "created_at": m.created_at,
            }
            for m in messages
        ]
        return Response(data)




@csrf_exempt
def chat_view(request):
    if request.method == "POST":
        data = json.loads(request.body)
        user_msg = data.get("message")

        session_id = request.session.get("chat_session_id")
        if not session_id:
            session_id = str(uuid.uuid4())
            request.session["chat_session_id"] = session_id
        ChatMessage.objects.create(session_id=session_id, role="user", message=user_msg)
        bot_response = "این فقط نمونه است، GPT بعداً وصل می‌شود"

        ChatMessage.objects.create(session_id=session_id, role="bot", message=bot_response)
        return JsonResponse({"response": bot_response})

    return JsonResponse({"error": "متد نامعتبر"}, status=405)



    
    
    
def search_product(query):
    products = fetch_products()
    results = []
    query_lower = query.lower()
    for product in products:
        if query_lower in product["name"].lower() or (
            product.get("categories") and query_lower in product["categories"][0].lower()
        ):
            results.append(
                {
                    "id": product["id"],
                    "name": product["name"],
                    "price": product["finalPrice"],
                    "stock": product["stock_quantity"],
                    "url": f"/products/{product['id']}/",
                }
            )
    return results
