from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers import NestedDefaultRouter

from api.views import ListConfigurationViewSet, ListDataViewSet, ListItemViewSet, ListConfigurationFieldViewSet

router = DefaultRouter()
router.register(r'configurations', ListConfigurationViewSet, basename='configuration')
router.register(r'data', ListDataViewSet, basename='data')

item_router = NestedDefaultRouter(router, r'data', lookup='list')
item_router.register(r'items', ListItemViewSet, basename='list-items')

field_router = NestedDefaultRouter(router, r'configurations', lookup='configuration')
field_router.register(r'fields', ListConfigurationFieldViewSet, basename='configuration-fields')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(item_router.urls)),
    path('', include(field_router.urls)),
]