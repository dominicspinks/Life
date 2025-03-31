from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ListConfigurationViewSet, ListDataViewSet, ListItemViewSet

router = DefaultRouter()
router.register(r'configurations', ListConfigurationViewSet, basename='configuration')
router.register(r'data', ListDataViewSet, basename='data')

urlpatterns = [
    path('', include(router.urls)),
    path('data/<int:list_id>/items/', ListItemViewSet.as_view({'get': 'list', 'post': 'create'}), name='list-items'),
    path('data/<int:list_id>/items/<int:pk>/', ListItemViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='list-item-detail'),
]