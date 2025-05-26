from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from api.models import FieldType, ListField, ListFieldOption, ListFieldRule, ListItem
from api.serializers.serializers_modules import UserModuleSerializer
from api.serializers.serializers_reference import FieldTypeRuleSerializer

User = get_user_model()

class ListFieldOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ListFieldOption
        fields = ['id', 'option_name']


class ListFieldRuleSerializer(serializers.ModelSerializer):
    field_type_rule = FieldTypeRuleSerializer(read_only=True)

    class Meta:
        model = ListFieldRule
        fields = ['id', 'field_type_rule']


class ListFieldSerializer(serializers.ModelSerializer):
    field_type = serializers.PrimaryKeyRelatedField(
        queryset=FieldType.objects.all()
    )
    field_type_name = serializers.StringRelatedField(source='field_type', read_only=True)
    rules = serializers.SerializerMethodField()
    options = serializers.SerializerMethodField()

    class Meta:
        model = ListField
        fields = [
            'id',
            'user_module',
            'field_name',
            'field_type',
            'field_type_name',
            'is_mandatory',
            'order',
            'rules',
            'options'
        ]

    @extend_schema_field(ListFieldRuleSerializer(many=True))
    def get_rules(self, obj):
        rules = ListFieldRule.objects.filter(list_field=obj)
        return ListFieldRuleSerializer(rules, many=True).data

    @extend_schema_field(ListFieldOptionSerializer(many=True))
    def get_options(self, obj):
        # Only return options if this is a dropdown field
        if obj.field_type.name == 'dropdown':
            options = ListFieldOption.objects.filter(list_field=obj)
            return ListFieldOptionSerializer(options, many=True).data
        return []


class ListConfigurationSerializer(UserModuleSerializer):
    list_fields = serializers.SerializerMethodField()

    class Meta(UserModuleSerializer.Meta):
        fields = UserModuleSerializer.Meta.fields + ['list_fields']

    @extend_schema_field(ListFieldSerializer(many=True))
    def get_list_fields(self, obj):
        list_fields = ListField.objects.filter(user_module=obj).order_by('order')
        return ListFieldSerializer(list_fields, many=True).data


class ListItemSerializer(serializers.ModelSerializer):
    field_values = serializers.JSONField(source='fields')

    class Meta:
        model = ListItem
        fields = ['id', 'is_completed', 'modified_at', 'field_values']
        read_only_fields = ['modified_at']

    def validate_field_values(self, value):
        # Validate that the objects in field_values are valid
        if not isinstance(value, list):
            raise serializers.ValidationError("Must be a list of field objects")

        for item in value:
            if not isinstance(item, dict):
                raise serializers.ValidationError("Each item must be an object")

            if 'field' not in item:
                raise serializers.ValidationError("Each item must have a 'field' property")

            if 'value' not in item:
                raise serializers.ValidationError("Each item must have a 'value' property")

        return value


class ListDataSerializer(ListConfigurationSerializer):
    list_items = serializers.SerializerMethodField()

    class Meta(ListConfigurationSerializer.Meta):
        fields = ListConfigurationSerializer.Meta.fields + ['list_items']

    @extend_schema_field(ListItemSerializer(many=True))
    def get_list_items(self, obj):
        list_items = ListItem.objects.filter(user_module=obj)
        return ListItemSerializer(list_items, many=True).data
