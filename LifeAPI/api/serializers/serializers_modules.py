from django.contrib.auth import get_user_model
from rest_framework import serializers

from api.models import ModuleType, UserModule

User = get_user_model()

class ModuleTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ModuleType
        fields = ['id', 'name']

class UserModuleSerializer(serializers.ModelSerializer):
    module_name = serializers.CharField(source='module.name', read_only=True)

    class Meta:
        model = UserModule
        fields = [
            'id',
            'module',
            'module_name',
            'name',
            'order',
            'is_enabled',
            'is_read_only',
            'is_checkable',
            'created_at',
            'modified_at'
        ]
        read_only_fields = ['created_at', 'modified_at']
