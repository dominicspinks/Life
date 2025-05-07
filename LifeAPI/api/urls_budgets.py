from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BudgetCategoryViewSet, BudgetPurchaseViewSet, BudgetViewSet
from rest_framework_nested.routers import NestedDefaultRouter

router = DefaultRouter()
router.register(r'', BudgetViewSet, basename='budget_root')

nested_router = NestedDefaultRouter(router, r'', lookup='budget')
nested_router.register(r'categories', BudgetCategoryViewSet, basename='budget-category')
nested_router.register(r'purchases', BudgetPurchaseViewSet, basename='budget-purchase')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(nested_router.urls)),
]