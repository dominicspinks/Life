from django.shortcuts import get_object_or_404
from django.http import Http404
from django_filters.rest_framework import DjangoFilterBackend
from django.db import transaction, connection
from django.utils.timezone import now
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.filters import OrderingFilter
from rest_framework.mixins import CreateModelMixin
from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema_view, extend_schema

from datetime import datetime

from api.serializers.serializers_budgets import BudgetCategorySerializer, BudgetPurchaseSerializer, BudgetSerializer, BudgetPurchaseSummarySerializer
from api.models import BudgetCategory, BudgetPurchase, UserModule
from api.pagination import Unpaginatable
from api.filters import PurchaseFilterSet

class BudgetViewSet(viewsets.ModelViewSet):
    """
    API endpoint for viewing and updating budget details
    """
    queryset = UserModule.objects.none()
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
    queryset = BudgetCategory.objects.none()
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

    @action(detail=True, methods=['post'], url_path='reorder')
    def reorder(self, request, budget_id=None, id=None):
        """
        Reorders a category by moving it to a new position within the list.
        Expects 'new_order' in the request body.
        """
        new_order = request.data.get('new_order')

        if new_order is None:
            return Response({'detail': 'new_order is required.'}, status=400)

        try:
            new_order = int(new_order)
        except ValueError:
            return Response({'detail': 'Invalid order value.'}, status=400)

        # Validate user and category ownership
        user_module = get_object_or_404(UserModule, id=budget_id, user=self.request.user)
        categories = list(BudgetCategory.objects.filter(user_module=user_module).order_by('order'))

        # Move category within the list
        category = get_object_or_404(BudgetCategory, id=id, user_module=user_module)
        original_order = category.order

        if original_order != new_order:
            moved_category = categories.pop(original_order - 1)
            categories.insert(new_order - 1, moved_category)

            # Reassign orders
            with transaction.atomic():
                for idx, cat in enumerate(categories):
                    cat.order = idx + 1
                BudgetCategory.objects.bulk_update(categories, ['order'])

        # Return updated budget config
        serializer = BudgetSerializer(user_module, context={'request': request})
        return Response(serializer.data, status=200)


class BudgetPurchaseViewSet(viewsets.ModelViewSet):
    """
    API endpoint for CRUD operations on budget purchases
    Allows users to view, create, update and delete their budget purchases
    """
    queryset = BudgetPurchase.objects.none()
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

@extend_schema_view(
    create=extend_schema(
        summary="Bulk create purchases",
        description="Imports a list of purchases into the given budget.",
        responses={201: BudgetPurchaseSerializer(many=True)},
    ),
    list=extend_schema(exclude=True),
    retrieve=extend_schema(exclude=True),
    update=extend_schema(exclude=True),
    partial_update=extend_schema(exclude=True),
    destroy=extend_schema(exclude=True),
)
class BudgetPurchaseBulkViewSet(viewsets.GenericViewSet, CreateModelMixin):
    """
    API endpoint for bulk importing purchases into a budget
    Only supports POST
    """
    queryset = BudgetPurchase.objects.none()
    serializer_class = BudgetPurchaseSerializer
    permission_classes = [permissions.IsAuthenticated]

    lookup_field = 'id'
    lookup_value_regex = r'\d+'

    def get_serializer_context(self):
        budget_id = self.kwargs.get('budget_id')
        user_module = get_object_or_404(UserModule, id=budget_id, user=self.request.user)
        return {**super().get_serializer_context(), 'user_module': user_module}

    def create(self, request, *args, **kwargs):
        data = request.data
        if not isinstance(data, list):
            return Response({"detail": "Expected a list of items."}, status=status.HTTP_400_BAD_REQUEST)

        context = self.get_serializer_context()
        serializer = self.get_serializer(data=data, many=True, context=context)
        serializer.is_valid(raise_exception=True)
        self.perform_bulk_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def perform_bulk_create(self, serializer):
        # Assumes user_module is injected via context
        user_module = self.get_serializer_context()['user_module']
        serializer.save(user_module=user_module)

    def list(self, request, *args, **kwargs):
        return Response({"detail": "Method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def retrieve(self, request, *args, **kwargs):
        return Response({"detail": "Method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def update(self, request, *args, **kwargs):
        return Response({"detail": "Method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def partial_update(self, request, *args, **kwargs):
        return Response({"detail": "Method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def destroy(self, request, *args, **kwargs):
        return Response({"detail": "Method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


class BudgetPurchaseSummaryViewSet(viewsets.GenericViewSet):
    """
    API endpoint for retrieving summary data for a budget
    """
    queryset = UserModule.objects.none()
    serializer_class = BudgetPurchaseSummarySerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None

    def list(self, request, budget_id=None):
        try:
            user_module = UserModule.objects.get(id=budget_id, user=request.user)
        except UserModule.DoesNotExist:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)

        start = request.query_params.get('start_date')
        end = request.query_params.get('end_date')

        # Validate date inputs
        try:
            start_date = datetime.strptime(start, "%Y-%m-%d").date()
            end_date = datetime.strptime(end, "%Y-%m-%d").date()
        except (TypeError, ValueError):
            return Response({'detail': 'start_date and end_date must be in YYYY-MM-DD format.'}, status=status.HTTP_400_BAD_REQUEST)

        query = """
            SELECT
                CAST(to_char(purchase_date,'IW') as int) AS week,
                category_id,
                SUM(amount) AS total
            FROM api_budgetpurchase
            WHERE user_module_id = %s
              AND purchase_date >= %s
              AND purchase_date < %s
            GROUP BY week, category_id
            ORDER BY week, category_id
        """

        with connection.cursor() as cursor:
            cursor.execute(query, [budget_id, start_date, end_date])
            results = cursor.fetchall()

        data = [
            {"week": row[0], "category": row[1], "total": float(row[2])}
            for row in results
        ]

        serializer = self.get_serializer(data, many=True)
        return Response(serializer.data)


    @action(detail=False, methods=['get'], url_path='years')
    def list_years(self, request, budget_id=None):
        try:
            user_module = UserModule.objects.get(id=budget_id, user=request.user)
        except UserModule.DoesNotExist:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)

        query = """
            SELECT DISTINCT EXTRACT(YEAR FROM purchase_date)::int AS year
            FROM api_budgetpurchase
            WHERE user_module_id = %s
            ORDER BY year
        """
        with connection.cursor() as cursor:
            cursor.execute(query, [user_module.id])
            rows = cursor.fetchall()

        years = sorted({int(row[0]) for row in rows})
        return Response(years)