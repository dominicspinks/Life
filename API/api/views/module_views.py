from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from ..models import ModuleType, UserModule
from ..serializers import ModuleTypeSerializer, UserModuleSerializer

class ModuleTypeViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for viewing module types.
    Provides read-only access to all available module types.
    """
    queryset = ModuleType.objects.all()
    serializer_class = ModuleTypeSerializer
    permission_classes = [permissions.IsAuthenticated]


class UserModuleViewSet(viewsets.ModelViewSet):
    """
    API endpoint for CRUD operations on user modules.
    Allows users to view, create, update and delete their modules.
    """
    serializer_class = UserModuleSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Return modules that belong to the current authenticated user
        """
        return UserModule.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """
        When creating a new module, automatically set the user to the current user
        """
        serializer.save(user=self.request.user)