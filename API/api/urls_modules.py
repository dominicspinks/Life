from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import module_views

router = DefaultRouter()
router.register(r'types', module_views.ModuleTypeViewSet)
router.register(r'user-modules', module_views.UserModuleViewSet, basename='user-module')

urlpatterns = [
    path('', include(router.urls)),
]