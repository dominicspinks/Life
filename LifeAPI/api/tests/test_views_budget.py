from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model

from api.models import (
    ModuleType, UserModule,
    BudgetCategory, BudgetPurchase
)

User = get_user_model()

class BudgetViewSetTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='user@example.com', password='password123')
        self.budget_type = ModuleType.objects.get(name='budget')

        self.budget1 = UserModule.objects.create(user=self.user, module=self.budget_type, name='Budget A', order=0, is_enabled=True)
        self.budget2 = UserModule.objects.create(user=self.user, module=self.budget_type, name='Budget B', order=1, is_enabled=True)

        self.base_url = f'/api/budgets/'

    def test_unauthenticated(self):
        response = self.client.get(self.base_url)
        self.assertEqual(response.status_code, 401)

    def test_list_budgets(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.base_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

    def test_retrieve_budget(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(f'{self.base_url}{self.budget1.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Budget A')

    def test_create_budget_not_allowed(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.base_url, data={})
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete_budget_not_allowed(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(f'{self.base_url}{self.budget1.id}/')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class BudgetCategoryViewSetTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='user@example.com', password='password123')
        self.budget_type = ModuleType.objects.get(name='budget')

        self.budget = UserModule.objects.create(user=self.user, module=self.budget_type, name='Main Budget', order=0, is_enabled=True)
        self.category = BudgetCategory.objects.create(user_module=self.budget, name='Groceries', weekly_target=100, order=0)

        self.base_url = f'/api/budgets/{self.budget.id}/categories/'

    def test_unauthenticated(self):
        response = self.client.get(self.base_url)
        self.assertEqual(response.status_code, 401)

    def test_list_categories(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.base_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_retrieve_category(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(f'{self.base_url}{self.category.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Groceries')

    def test_create_category(self):
        self.client.force_authenticate(user=self.user)
        data = {
            'name': 'Utilities',
            'weekly_target': 50,
            'excluded_from_budget': False,
            'order': 1,
            'is_enabled': True
        }
        response = self.client.post(self.base_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Utilities')

    def test_update_category(self):
        self.client.force_authenticate(user=self.user)
        data = {
            'name': 'Groceries Updated',
            'weekly_target': 120,
            'excluded_from_budget': True,
            'order': 0,
            'is_enabled': False
        }
        response = self.client.put(f'{self.base_url}{self.category.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Groceries Updated')

    def test_delete_category(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(f'{self.base_url}{self.category.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(BudgetCategory.objects.filter(id=self.category.id).exists())


class BudgetPurchaseViewSetTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='user@example.com', password='password123')
        self.budget_type = ModuleType.objects.get(name='budget')

        self.budget = UserModule.objects.create(user=self.user, module=self.budget_type, name='Main Budget', order=0, is_enabled=True)
        self.category = BudgetCategory.objects.create(user_module=self.budget, name='Groceries', weekly_target=100, order=0)
        self.purchase = BudgetPurchase.objects.create(
            user_module=self.budget,
            purchase_date='2024-01-01',
            amount=50.00,
            description='Woolworths',
            category=self.category
        )

        self.base_url = f'/api/budgets/{self.budget.id}/purchases/'

    def test_unauthenticated(self):
        response = self.client.get(self.base_url)
        self.assertEqual(response.status_code, 401)

    def test_list_purchases(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.base_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_retrieve_purchase(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(f'{self.base_url}{self.purchase.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['description'], 'Woolworths')

    def test_create_purchase(self):
        self.client.force_authenticate(user=self.user)
        data = {
            'purchase_date': '2024-02-01',
            'amount': 30.00,
            'description': 'Aldi',
            'category': self.category.id
        }
        response = self.client.post(self.base_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['description'], 'Aldi')

    def test_update_purchase(self):
        self.client.force_authenticate(user=self.user)
        data = {
            'purchase_date': '2024-01-01',
            'amount': 75.00,
            'description': 'Updated Purchase',
            'category': self.category.id
        }
        response = self.client.put(f'{self.base_url}{self.purchase.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['amount'], '75.00')

    def test_delete_purchase(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(f'{self.base_url}{self.purchase.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(BudgetPurchase.objects.filter(id=self.purchase.id).exists())

    def test_invalid_category(self):
        self.client.force_authenticate(user=self.user)
        other_budget = UserModule.objects.create(user=self.user, module=self.budget_type, name='Other Budget', order=1, is_enabled=True)
        other_category = BudgetCategory.objects.create(user_module=other_budget, name='Other', weekly_target=50, order=0)

        data = {
            'purchase_date': '2024-03-01',
            'amount': 10.00,
            'description': 'Invalid Cat',
            'category': other_category.id
        }
        response = self.client.post(self.base_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('category', response.data)
