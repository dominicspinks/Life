from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from api.models import FieldType, FieldTypeRule, Period

User = get_user_model()

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

class PeriodSerializer(serializers.ModelSerializer):
    class Meta:
        model = Period
        fields = ['id', 'name']
        read_only_fields = ['id', 'name']