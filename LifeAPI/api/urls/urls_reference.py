from django.urls import path, include
from rest_framework.routers import DefaultRouter

from api.views import FieldTypeViewSet

router = DefaultRouter()
router.register(r'field-types', FieldTypeViewSet, basename='field-type')

urlpatterns = [
    path('', include(router.urls)),
]