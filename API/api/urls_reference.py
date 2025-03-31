from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import reference_views


router = DefaultRouter()
router.register(r'field-types', reference_views.FieldTypeViewSet, basename='field-type')
router.register(r'field-type-details', reference_views.FieldTypeViewSet, basename='field-type-full')

urlpatterns = [
    path('', include(router.urls)),
]