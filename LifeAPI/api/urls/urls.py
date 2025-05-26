from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework.routers import DefaultRouter

router = DefaultRouter()

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('api.urls.urls_auth')),
    path('modules/', include('api.urls.urls_modules')),
    path('lists/', include('api.urls.urls_lists')),
    path('reference/', include('api.urls.urls_reference')),
    path('budgets/', include('api.urls.urls_budgets')),
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('schema/swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger')
]