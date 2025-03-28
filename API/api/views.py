from rest_framework import viewsets, generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth.models import User
from .serializers import RegisterSerializer

# Registration view
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

# Logout view
from rest_framework.views import APIView

class LogoutView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        return Response(
            {"detail": "Successfully logged out."},
            status=status.HTTP_200_OK
        )