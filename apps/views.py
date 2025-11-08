from django.http import JsonResponse
from drf_spectacular.utils import extend_schema
from rest_framework.generics import ListAPIView
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from apps.serializer import RegisterModelSerializer
from apps.models import Lead
from rest_framework.permissions import IsAuthenticated

@extend_schema(tags=["register"],request=RegisterModelSerializer)
class RegisterApiView(APIView):
    def post(self,request):
        serializer = RegisterModelSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse({"message":"Siz ruyxatdan utdingiz"})
        return JsonResponse({"message":"Bunday raqamdan oldin ruyxatdan o'tgan"})


@extend_schema(tags=["login"])
class CustomTokenObtainPairView(TokenObtainPairView):
    pass

@extend_schema(tags=["login"])
class CustomTokenRefreshView(TokenRefreshView):
    pass

@extend_schema(tags=["list"])
class ListApiView(ListAPIView):
    queryset = Lead.objects.all()
    serializer_class = RegisterModelSerializer
    permission_classes = [IsAuthenticated]
