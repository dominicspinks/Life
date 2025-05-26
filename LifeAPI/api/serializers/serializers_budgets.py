from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from api.models import BudgetCategory, BudgetPurchase
from api.serializers.serializers_modules import UserModuleSerializer

User = get_user_model()

class BudgetCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = BudgetCategory
        fields = [
            'id',
            'name',
            'weekly_target',
            'excluded_from_budget',
            'order',
            'is_enabled',
            'created_at',
            'modified_at'
        ]
        read_only_fields = ['created_at', 'modified_at']

    def validate(self, attrs):
        # Check if a category with the same name already exists
        user_module = self.context.get('user_module')
        name = attrs.get('name')
        if user_module and name:
            qs = BudgetCategory.objects.filter(user_module=user_module, name=name)
            if self.instance:
                qs = qs.exclude(id=self.instance.id)
            if qs.exists():
                raise serializers.ValidationError({'name': "A category with this name already exists."})

        return attrs


class BudgetPurchaseSerializer(serializers.ModelSerializer):
    category_name = serializers.StringRelatedField(source='category', read_only=True)

    class Meta:
        model = BudgetPurchase
        fields = [
            'id',
            'purchase_date',
            'amount',
            'description',
            'category',
            'category_name',
            'modified_at'
        ]
        read_only_fields = ['category_name', 'modified_at']

    def validate(self, attrs):
        user_module = self.context.get('user_module')
        category = attrs.get('category')

        if category and category.user_module_id != user_module.id:
            raise serializers.ValidationError({
                'category': 'This category does not belong to the current budget.'
            })

        return attrs

    def create(self, validated_data):
        user_module = self.context.get('user_module')
        if isinstance(validated_data, list):
            for item in validated_data:
                item['user_module'] = user_module
            return BudgetPurchase.objects.bulk_create(
                [BudgetPurchase(**item) for item in validated_data]
            )
        else:
            validated_data['user_module'] = user_module
            return super().create(validated_data)

class BudgetSerializer(UserModuleSerializer):
    categories = serializers.SerializerMethodField()

    class Meta(UserModuleSerializer.Meta):
        fields = UserModuleSerializer.Meta.fields + ['categories']

    @extend_schema_field(BudgetCategorySerializer(many=True))
    def get_categories(self, obj):
        categories = BudgetCategory.objects.filter(user_module=obj).order_by('order')
        return BudgetCategorySerializer(categories, many=True).data

class BudgetPurchaseSummarySerializer(serializers.Serializer):
    week = serializers.IntegerField()
    category = serializers.IntegerField()
    total = serializers.FloatField()