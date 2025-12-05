from django.shortcuts import render
import json
from django.http import StreamingHttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from openai import OpenAI

client = OpenAI(api_key="YOUR_API_KEY_HERE")


class ChatBotAPI(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        user_message = request.data.get("message")

        # اگر پیام خالی باشد
        if not user_message:
            return Response({"error": "پیامی ارسال نشده."}, status=400)

        # 🎯 پاسخ زنده (Streaming)
        def stream():
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                stream=True,
                messages=[
                    {"role": "system", "content": "تو یک پشتیبان فروشگاه هستی. مودب، سریع، فروشنده حرفه‌ای."},
                    {"role": "user", "content": user_message}
                ]
            )

            for chunk in response:
                if chunk.choices:
                    delta = chunk.choices[0].delta.get("content")
                    if delta:
                        yield f"{delta}"

        return StreamingHttpResponse(stream(), content_type="text/plain")
    
    
    
    
import json
import requests
from django.http import StreamingHttpResponse
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from openai import OpenAI
from .utils import fetch_products

client = OpenAI(api_key="YOUR_API_KEY")


class ChatBotView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        user_msg = request.data.get("message")

        products = fetch_products()

        system_prompt = f"""
تو یک پشتیبان حرفه‌ای فروشگاه هستی.

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
                    {"role": "user", "content": user_msg}
                ]
            )
            for chunk in response:
                if chunk.choices:
                    delta = chunk.choices[0].delta.get("content")
                    if delta:
                        yield delta
            
        return StreamingHttpResponse(stream(), content_type="text/plain")





from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from .models import ChatMessage

class ChatHistoryAdminView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        messages = ChatMessage.objects.all().order_by("-created_at")[:200]  # آخرین ۲۰۰ پیام
        data = [
            {
                "session_id": m.session_id,
                "role": m.role,
                "message": m.message,
                "created_at": m.created_at
            } for m in messages
        ]
        return Response(data)


from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json, uuid
from .models import ChatMessage

@csrf_exempt
def chat_view(request):
    if request.method == "POST":
        data = json.loads(request.body)
        user_msg = data.get("message")

        # مدیریت session
        session_id = request.session.get("chat_session_id")
        if not session_id:
            session_id = str(uuid.uuid4())
            request.session["chat_session_id"] = session_id

        # ذخیره پیام کاربر
        ChatMessage.objects.create(
            session_id=session_id,
            role="user",
            message=user_msg
        )

        # --- اینجا پیام را به GPT ارسال کن و پاسخ بگیر ---
        # bot_response = call_your_gpt_function(user_msg)
        bot_response = "این فقط نمونه است، GPT بعداً وصل می‌شود"

        # ذخیره پاسخ چت‌بات
        ChatMessage.objects.create(
            session_id=session_id,
            role="bot",
            message=bot_response
        )

        return JsonResponse({"response": bot_response})


import requests

def get_products():
    try:
        response = requests.get("http://127.0.0.1:8000/products/api/list/")
        response.raise_for_status()
        products = response.json()
        return products
    except requests.RequestException:
        return []
    
    
    
def search_product(query):
    products = get_products()
    results = []
    query_lower = query.lower()
    for p in products:
        if query_lower in p["name"].lower() or query_lower in p["categories"][0]["title"].lower():
            results.append({
                "id": p["id"],
                "name": p["name"],
                "price": p["finalPrice"],
                "stock": p["stock_quantity"],
                "url": f"/products/{p['id']}/",
            })
    return results
