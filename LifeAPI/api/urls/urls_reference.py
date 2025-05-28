from django.urls import path, include
from rest_framework.routers import DefaultRouter

from api.views import FieldTypeViewSet, PeriodViewSet

router = DefaultRouter()
router.register(r'field-types', FieldTypeViewSet, basename='field-type')
router.register(r'periods', PeriodViewSet, basename='period')

urlpatterns = [
    path('', include(router.urls)),
]