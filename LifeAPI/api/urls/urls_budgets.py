from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers import NestedDefaultRouter

from api.views import (
    BudgetCategoryViewSet,
    BudgetPurchaseViewSet,
    BudgetViewSet,
    BudgetPurchaseBulkViewSet,
    BudgetPurchaseSummaryViewSet,
    BudgetCashFlowViewSet
)


router = DefaultRouter()
router.register(r'', BudgetViewSet, basename='budget_root')

nested_router = NestedDefaultRouter(router, r'', lookup='budget')
nested_router.register(r'categories', BudgetCategoryViewSet, basename='budget-category')
nested_router.register(r'purchases', BudgetPurchaseViewSet, basename='budget-purchase')
nested_router.register(r'purchases/bulk', BudgetPurchaseBulkViewSet, basename='budget-purchase-bulk')
nested_router.register(r'summary', BudgetPurchaseSummaryViewSet, basename='budget-summary')
nested_router.register(r'cashflows', BudgetCashFlowViewSet, basename='budget-cashflow')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(nested_router.urls)),
]