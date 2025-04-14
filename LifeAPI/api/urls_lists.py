from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ListConfigurationViewSet, ListDataViewSet, ListItemViewSet
from rest_framework_nested.routers import NestedDefaultRouter

router = DefaultRouter()
router.register(r'configurations', ListConfigurationViewSet, basename='configuration')
router.register(r'data', ListDataViewSet, basename='data')

item_router = NestedDefaultRouter(router, r'data', lookup='list')
item_router.register(r'items', ListItemViewSet, basename='list-item')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(item_router.urls)),
]