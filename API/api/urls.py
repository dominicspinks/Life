from django.urls import path, include
from rest_framework.routers import DefaultRouter

router = DefaultRouter()

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('api.urls_auth')),
    path('modules/', include('api.urls_modules')),
    path('lists/', include('api.urls_lists')),
    path('reference/', include('api.urls_reference')),
]