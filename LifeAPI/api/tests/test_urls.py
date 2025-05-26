from django.test import TestCase
from django.urls import reverse, resolve
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from api.views import (
    RegisterView,
    LogoutView,
    ListItemViewSet,
    BudgetViewSet,
    BudgetCategoryViewSet,
    BudgetPurchaseViewSet,
    BudgetPurchaseBulkViewSet,
    BudgetPurchaseSummaryViewSet,
    FieldTypeViewSet,
    ModuleTypeViewSet,
    UserModuleViewSet,
    ListConfigurationViewSet,
    ListDataViewSet,
    ListConfigurationFieldViewSet
)

class AuthURLTests(TestCase):
    """Test authentication URL patterns."""

    def test_login_urls(self):
        url = reverse('token_obtain_pair')
        self.assertEqual(url, '/api/auth/login/')
        self.assertEqual(resolve(url).func.cls, TokenObtainPairView)

    def test_toekn_refresh_urls(self):
        url = reverse('token_refresh')
        self.assertEqual(url, '/api/auth/login/refresh/')
        self.assertEqual(resolve(url).func.cls, TokenRefreshView)

    def test_register_urls(self):
        url = reverse('auth_register')
        self.assertEqual(url, '/api/auth/register/')
        self.assertEqual(resolve(url).func.cls, RegisterView)

    def test_logout_urls(self):
        url = reverse('auth_logout')
        self.assertEqual(url, '/api/auth/logout/')
        self.assertEqual(resolve(url).func.cls, LogoutView)


class ModuleURLTests(TestCase):
    """Test module-related URL patterns."""

    def test_module_type_urls(self):
        url = reverse('moduletype-list')
        self.assertEqual(url, '/api/modules/types/')
        self.assertEqual(resolve(url).func.cls, ModuleTypeViewSet)

        url = reverse('moduletype-detail', args=[1])
        self.assertEqual(url, '/api/modules/types/1/')
        self.assertEqual(resolve(url).func.cls, ModuleTypeViewSet)

    def test_user_module_urls(self):
        url = reverse('user-module-list')
        self.assertEqual(url, '/api/modules/user-modules/')
        self.assertEqual(resolve(url).func.cls, UserModuleViewSet)

        url = reverse('user-module-detail', args=[1])
        self.assertEqual(url, '/api/modules/user-modules/1/')
        self.assertEqual(resolve(url).func.cls, UserModuleViewSet)


class ListURLTests(TestCase):
    """Test list-related URL patterns."""

    def test_configuration_urls(self):
        url = reverse('configuration-list')
        self.assertEqual(url, '/api/lists/configurations/')
        self.assertEqual(resolve(url).func.cls, ListConfigurationViewSet)

        url = reverse('configuration-detail', args=[1])
        self.assertEqual(url, '/api/lists/configurations/1/')
        self.assertEqual(resolve(url).func.cls, ListConfigurationViewSet)

    def test_data_urls(self):
        url = reverse('data-list')
        self.assertEqual(url, '/api/lists/data/')
        self.assertEqual(resolve(url).func.cls, ListDataViewSet)

        url = reverse('data-detail', args=[1])
        self.assertEqual(url, '/api/lists/data/1/')
        self.assertEqual(resolve(url).func.cls, ListDataViewSet)

    def test_items_urls(self):
        url = reverse('list-items-list', args=[1])
        self.assertEqual(url, '/api/lists/data/1/items/')
        self.assertEqual(resolve(url).func.cls, ListItemViewSet)

        url = reverse('list-items-detail', args=[1, 2])
        self.assertEqual(url, '/api/lists/data/1/items/2/')
        self.assertEqual(resolve(url).func.cls, ListItemViewSet)

    def test_field_urls(self):
        url = reverse('configuration-fields-list', args=[1])
        self.assertEqual(url, '/api/lists/configurations/1/fields/')
        self.assertEqual(resolve(url).func.cls, ListConfigurationFieldViewSet)

        url = reverse('configuration-fields-detail', args=[1, 2])
        self.assertEqual(url, '/api/lists/configurations/1/fields/2/')
        self.assertEqual(resolve(url).func.cls, ListConfigurationFieldViewSet)

    def test_nested_resolution(self):
        resolver = resolve('/api/lists/data/1/items/2/')
        self.assertEqual(resolver.func.cls, ListItemViewSet)
        self.assertEqual(resolver.kwargs['list_id'], '1')
        self.assertEqual(resolver.kwargs['id'], '2')

class ReferenceURLTests(TestCase):
    """Test reference data URL patterns."""

    def test_field_type_urls(self):
        url = reverse('field-type-list')
        self.assertEqual(url, '/api/reference/field-types/')
        self.assertEqual(resolve(url).func.cls, FieldTypeViewSet)

        url = reverse('field-type-detail', args=[1])
        self.assertEqual(url, '/api/reference/field-types/1/')
        self.assertEqual(resolve(url).func.cls, FieldTypeViewSet)


class BudgetURLTests(TestCase):
    """Test URL configurations for budget-related endpoints."""

    def test_budget_urls(self):
        """Test budget root viewset URLs."""
        url = reverse('budget_root-list')
        self.assertEqual(url, '/api/budgets/')
        self.assertEqual(resolve(url).func.cls, BudgetViewSet)

        url = reverse('budget_root-detail', args=[1])
        self.assertEqual(url, '/api/budgets/1/')
        self.assertEqual(resolve(url).func.cls, BudgetViewSet)

    def test_budget_category_urls(self):
        """Test nested budget category viewset URLs."""
        url = reverse('budget-category-list', args=[1])
        self.assertEqual(url, '/api/budgets/1/categories/')
        self.assertEqual(resolve(url).func.cls, BudgetCategoryViewSet)

        url = reverse('budget-category-detail', args=[1, 2])
        self.assertEqual(url, '/api/budgets/1/categories/2/')
        self.assertEqual(resolve(url).func.cls, BudgetCategoryViewSet)

    def test_budget_purchase_urls(self):
        """Test nested budget purchase viewset URLs."""
        url = reverse('budget-purchase-list', args=[1])
        self.assertEqual(url, '/api/budgets/1/purchases/')
        self.assertEqual(resolve(url).func.cls, BudgetPurchaseViewSet)

        url = reverse('budget-purchase-detail', args=[1, 2])
        self.assertEqual(url, '/api/budgets/1/purchases/2/')
        self.assertEqual(resolve(url).func.cls, BudgetPurchaseViewSet)

    def test_budget_nested_resolvers(self):
        """Check nested kwargs in budget-related routes."""
        resolver = resolve('/api/budgets/1/categories/2/')
        self.assertEqual(resolver.func.cls, BudgetCategoryViewSet)
        self.assertEqual(resolver.kwargs['budget_id'], '1')
        self.assertEqual(resolver.kwargs['id'], '2')

        resolver = resolve('/api/budgets/1/purchases/2/')
        self.assertEqual(resolver.func.cls, BudgetPurchaseViewSet)
        self.assertEqual(resolver.kwargs['budget_id'], '1')
        self.assertEqual(resolver.kwargs['id'], '2')

    def test_budget_bulk_purchase_urls(self):
        """Test nested budget bulk purchase viewset URLs."""
        url = reverse('budget-purchase-bulk-list', args=[1])
        self.assertEqual(url, '/api/budgets/1/purchases/bulk/')
        self.assertEqual(resolve(url).func.cls, BudgetPurchaseBulkViewSet)

    def test_budget_summary_urls(self):
        """Test nested budget summary viewset URLs."""
        url = reverse('budget-summary-list', args=[1])
        self.assertEqual(url, '/api/budgets/1/summary/')
        self.assertEqual(resolve(url).func.cls, BudgetPurchaseSummaryViewSet)

    def test_budget_summary_resolver_kwargs(self):
        """Check nested kwargs in budget summary route."""
        resolver = resolve('/api/budgets/1/summary/')
        self.assertEqual(resolver.func.cls, BudgetPurchaseSummaryViewSet)
        self.assertEqual(resolver.kwargs['budget_id'], '1')

    def test_budget_summary_years_urls(self):
        """Test nested budget summary years endpoint URL."""
        url = reverse('budget-summary-list-years', args=[1])
        self.assertEqual(url, '/api/budgets/1/summary/years/')
        self.assertEqual(resolve(url).func.cls, BudgetPurchaseSummaryViewSet)

    def test_budget_summary_years_resolver_kwargs(self):
        """Check nested kwargs in budget summary years route."""
        resolver = resolve('/api/budgets/1/summary/years/')
        self.assertEqual(resolver.func.cls, BudgetPurchaseSummaryViewSet)
        self.assertEqual(resolver.kwargs['budget_id'], '1')
