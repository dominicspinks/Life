from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import list_views


router = DefaultRouter()
router.register(r'configurations', list_views.ListConfigurationViewSet, basename='configuration')
router.register(r'data', list_views.ListDataViewSet, basename='data')

urlpatterns = [
    path('', include(router.urls)),
    path('data/<int:list_id>/items/', list_views.ListItemViewSet.as_view({'get': 'list', 'post': 'create'}), name='list-items'),
    path('data/<int:list_id>/items/<int:pk>/', list_views.ListItemViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='list-item-detail'),
]