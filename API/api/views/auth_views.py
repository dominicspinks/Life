from rest_framework import viewsets, generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import get_user_model
from ..serializers import RegisterSerializer, EmailTokenObtainSerializer
from rest_framework.views import APIView

User = get_user_model()

# Registration view
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

# Email Login view
class EmailTokenObtainPairView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = EmailTokenObtainSerializer(data=request.data,
                                                context={'request': request})
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data)

# Logout view
class LogoutView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        return Response(
            {"detail": "Successfully logged out."},
            status=status.HTTP_200_OK
        )