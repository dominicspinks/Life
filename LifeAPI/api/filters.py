import django_filters
from .models import BudgetPurchase, BudgetCategory

class PurchaseFilterSet(django_filters.FilterSet):
    category = django_filters.ModelMultipleChoiceFilter(
        field_name='category',
        queryset=BudgetCategory.objects.all()
    )
    purchase_date__year = django_filters.NumberFilter(field_name='purchase_date', lookup_expr='year')
    purchase_date__month = django_filters.NumberFilter(field_name='purchase_date', lookup_expr='month')

    class Meta:
        model = BudgetPurchase
        fields = ['category', 'purchase_date__year', 'purchase_date__month']
