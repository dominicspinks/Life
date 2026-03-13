from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from django.shortcuts import get_object_or_404

from api.serializers.serializers_modules import ModuleTypeSerializer, UserModuleSerializer
from api.models import ModuleType, UserModule
from api.pagination import Unpaginatable

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
        return UserModule.objects.filter(user=self.request.user).order_by('order')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'], url_path='reorder')
    def reorder(self, request, id=None):
        """
        Reorders a user module by moving it to a new position.
        Expects 'new_order' in the request body.
        """
        new_order = request.data.get('new_order')

        if new_order is None:
            return Response({'detail': 'new_order is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            new_order = int(new_order)
        except ValueError:
            return Response({'detail': 'Invalid order value.'}, status=status.HTTP_400_BAD_REQUEST)

        modules = list(UserModule.objects.filter(user=request.user).order_by('order'))
        
        module = get_object_or_404(UserModule, id=id, user=request.user)
        original_order = module.order

        if original_order != new_order:
            moved_module = None
            for idx, m in enumerate(modules):
                if m.id == module.id:
                    moved_module = modules.pop(idx)
                    break
            
            if moved_module:
                insert_index = max(0, new_order - 1)
                modules.insert(insert_index, moved_module)

                with transaction.atomic():
                    for idx, m in enumerate(modules):
                        m.order = idx + 1
                    UserModule.objects.bulk_update(modules, ['order'])

        # Return updated module list so frontend can sync
        updated_modules = UserModule.objects.filter(user=request.user).order_by('order')
        serializer = self.get_serializer(updated_modules, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)