from rest_framework import viewsets, permissions

from api.serializers.serializers_reference import FieldTypeSerializer, FieldTypeDetailSerializer, PeriodSerializer
from api.models import FieldType, Period

class FieldTypeViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for viewing field types and their rules.
    Provides read-only access to all available field types.
    """
    queryset = FieldType.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None

    def get_serializer_class(self):
        if self.action == 'retrieve' or self.request.query_params.get('detailed') == 'true':
            return FieldTypeDetailSerializer
        return FieldTypeSerializer

class PeriodViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for viewing periods.
    Provides read-only access to all available periods.
    """
    queryset = Period.objects.all()
    serializer_class = PeriodSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None
