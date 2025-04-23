from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.tokens import RefreshToken
from .models import CustomUser, ModuleType, UserModule, FieldType, FieldTypeRule, ListField, ListFieldOption, ListFieldRule, ListItem
from drf_spectacular.utils import extend_schema_field

User = get_user_model()

## Auth
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])

    class Meta:
        model = CustomUser
        fields = ('email', 'password')

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user


class EmailTokenObtainSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            # Get the user by email
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                raise serializers.ValidationError("No user found with this email address.")

            # Authenticate with email and password
            user = authenticate(
                request=self.context.get('request'),
                email=user.email,
                password=password
            )

            if not user:
                raise serializers.ValidationError('Unable to log in with provided credentials.')
        else:
            raise serializers.ValidationError('Must include "email" and "password".')

        # Generate token
        refresh = RefreshToken.for_user(user)

        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': {
                'id': user.id,
                'email': user.email
            }
        }

class LogoutSerializer(serializers.Serializer):
    detail = serializers.CharField(read_only=True)

## Field Types
class FieldTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = FieldType
        fields = ['id', 'name']

class FieldTypeRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = FieldTypeRule
        fields = ['id', 'rule']

class FieldTypeDetailSerializer(serializers.ModelSerializer):
    rules = serializers.SerializerMethodField()

    class Meta:
        model = FieldType
        fields = ['id', 'name', 'rules']

    @extend_schema_field(FieldTypeRuleSerializer(many=True))
    def get_rules(self, obj):
        rules = FieldTypeRule.objects.filter(field_type=obj)
        return FieldTypeRuleSerializer(rules, many=True).data

## Modules
class ModuleTypeSerializer(serializers.ModelSerializer):
    """Serializer for ModuleType objects"""
    class Meta:
        model = ModuleType
        fields = ['id', 'name']


class UserModuleSerializer(serializers.ModelSerializer):
    # Add the module type name as a read-only field
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

## Lists
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