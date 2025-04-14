from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ModuleTypeViewSet, UserModuleViewSet

router = DefaultRouter()
router.register(r'types', ModuleTypeViewSet)
router.register(r'user-modules', UserModuleViewSet, basename='user-module')

urlpatterns = [
    path('', include(router.urls)),
]