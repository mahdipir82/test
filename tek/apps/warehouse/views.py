from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Stock, StockMovement
from .serializers import StockSerializer, StockMovementSerializer

class StockListAPIView(generics.ListAPIView):
    queryset = Stock.objects.all()
    serializer_class = StockSerializer


class StockMovementAPIView(APIView):
    def post(self, request):
        serializer = StockMovementSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"success": True, "message": "موجودی بروزرسانی شد"}, status=status.HTTP_201_CREATED)
        return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
