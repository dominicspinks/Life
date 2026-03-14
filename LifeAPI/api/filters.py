import django_filters

from api.models import BudgetPurchase, BudgetCategory

class PurchaseFilterSet(django_filters.FilterSet):
    category = django_filters.ModelMultipleChoiceFilter(
        field_name='category',
        queryset=BudgetCategory.objects.all()
    )
    purchase_date__year = django_filters.NumberFilter(field_name='purchase_date', lookup_expr='year')
    purchase_date__month = django_filters.NumberFilter(field_name='purchase_date', lookup_expr='month')
    description = django_filters.CharFilter(field_name='description', lookup_expr='icontains')

    class Meta:
        model = BudgetPurchase
        fields = ['category', 'purchase_date__year', 'purchase_date__month', 'description']
