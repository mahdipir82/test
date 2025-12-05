from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import DiscountApplySerializer

class ApplyDiscountAPIView(APIView):
    def post(self, request):
        serializer = DiscountApplySerializer(data=request.data)
        if serializer.is_valid():
            return Response({
                "success": True,
                "final_price": serializer.validated_data['final_price'],
                "discount_amount": serializer.validated_data['discount_amount'],
                "message": "تخفیف با موفقیت اعمال شد."
            })
        return Response({
            "success": False,
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
