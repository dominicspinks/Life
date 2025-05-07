from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.filters import OrderingFilter
from ..serializers import BudgetCategorySerializer, BudgetPurchaseSerializer, BudgetSerializer
from ..models import BudgetCategory, BudgetPurchase, UserModule
from ..pagination import Unpaginatable
from ..filters import PurchaseFilterSet
from django.shortcuts import get_object_or_404
from django.http import Http404
from django_filters.rest_framework import DjangoFilterBackend

class BudgetViewSet(viewsets.ModelViewSet):
    """
    API endpoint for viewing and updating budget details
    """
    serializer_class = BudgetSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = Unpaginatable

    lookup_field = 'id'
    lookup_value_regex = r'\d+'

    def get_queryset(self):
        """
        Return budgets that belong to the current authenticated user
        """
        return UserModule.objects.filter(user=self.request.user, module__name='budget')

    def create(self, request, *args, **kwargs):
        return Response(
            {"detail": "Budget creation is handled through the /api/modules/ endpoint."},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )

    def destroy(self, request, *args, **kwargs):
        return Response(
            {"detail": "Budget deletion is handled through the /api/modules/ endpoint."},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )

class BudgetCategoryViewSet(viewsets.ModelViewSet):
    """
    API endpoint for CRUD operations on budget categories
    Allows users to view, create, update and delete their budget categories
    """
    serializer_class = BudgetCategorySerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None

    lookup_field = 'id'
    lookup_value_regex = r'\d+'

    def get_queryset(self):
        """
        Return categories that belong to the current authenticated user
        """
        budget_id = self.kwargs.get('budget_id')
        if not UserModule.objects.filter(id=budget_id, user=self.request.user).exists():
            raise Http404("Budget not found.")
        return BudgetCategory.objects.filter(user_module__id=budget_id, user_module__user=self.request.user).order_by('order')

    def get_serializer_context(self):
        # Include the user module in the serializer context
        context = super().get_serializer_context()
        budget_id = self.kwargs.get('budget_id')
        user_module = get_object_or_404(UserModule, id=budget_id, user=self.request.user)
        context['user_module'] = user_module
        return context

    def perform_create(self, serializer):
        serializer.save(user_module=self.get_serializer_context()['user_module'])


class BudgetPurchaseViewSet(viewsets.ModelViewSet):
    """
    API endpoint for CRUD operations on budget purchases
    Allows users to view, create, update and delete their budget purchases
    """
    serializer_class = BudgetPurchaseSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = Unpaginatable
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = PurchaseFilterSet
    ordering_fields = ['purchase_date', 'amount', 'category__name']
    ordering = ['-purchase_date']

    lookup_field = 'id'
    lookup_value_regex = r'\d+'

    def get_queryset(self):
        budget_id = self.kwargs.get('budget_id')
        if not UserModule.objects.filter(id=budget_id, user=self.request.user).exists():
            raise Http404("Budget not found.")
        return BudgetPurchase.objects.filter(user_module__id=budget_id, user_module__user=self.request.user)

    def get_serializer_context(self):
        # Include the user module in the serializer context
        context = super().get_serializer_context()
        budget_id = self.kwargs.get('budget_id')
        user_module = get_object_or_404(UserModule, id=budget_id, user=self.request.user)
        context['user_module'] = user_module
        return context

    def perform_create(self, serializer):
        serializer.save(user_module=self.get_serializer_context()['user_module'])