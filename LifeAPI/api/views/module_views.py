from rest_framework import viewsets, permissions
from ..models import ModuleType, UserModule
from ..serializers import ModuleTypeSerializer, UserModuleSerializer
from ..pagination import Unpaginatable

class ModuleTypeViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for viewing module types.
    Provides read-only access to all available module types.
    """
    queryset = ModuleType.objects.all()
    serializer_class = ModuleTypeSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = Unpaginatable


class UserModuleViewSet(viewsets.ModelViewSet):
    """
    API endpoint for CRUD operations on user modules.
    Allows users to view, create, update and delete their modules.
    """
    queryset = UserModule.objects.none()
    serializer_class = UserModuleSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = Unpaginatable

    lookup_field = 'id'
    lookup_value_regex = r'\d+'

    def get_queryset(self):
        return UserModule.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)