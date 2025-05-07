from django.urls import path, include
from rest_framework.routers import DefaultRouter
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

router = DefaultRouter()

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('api.urls_auth')),
    path('modules/', include('api.urls_modules')),
    path('lists/', include('api.urls_lists')),
    path('reference/', include('api.urls_reference')),
    path('budgets/', include('api.urls_budgets')),
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('schema/swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger')
]