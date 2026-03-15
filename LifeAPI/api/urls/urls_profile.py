from django.urls import path, include
from rest_framework.routers import DefaultRouter

from api.views import DeleteProfileView

router = DefaultRouter()

urlpatterns = [
    path('delete/', DeleteProfileView.as_view(), name='delete-profile'),
]
