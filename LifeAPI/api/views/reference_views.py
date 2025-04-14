from rest_framework import viewsets, permissions
from ..models import FieldType
from ..serializers import FieldTypeSerializer, FieldTypeDetailSerializer

class FieldTypeViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for viewing field types and their rules.
    Provides read-only access to all available field types.
    """
    queryset = FieldType.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'retrieve' or self.request.query_params.get('detailed') == 'true':
            return FieldTypeDetailSerializer
        return FieldTypeSerializer