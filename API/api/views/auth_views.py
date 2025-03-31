from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import get_user_model
from ..serializers import RegisterSerializer, EmailTokenObtainSerializer
from rest_framework.views import APIView

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    """
    API endpoint for user registration
    """
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

class EmailTokenObtainPairView(APIView):
    """
    API endpoint for user login
    """
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = EmailTokenObtainSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data)

class LogoutView(APIView):
    """
    API endpoint for user logout
    """
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        return Response(
            {"detail": "Successfully logged out."},
            status=status.HTTP_200_OK
        )