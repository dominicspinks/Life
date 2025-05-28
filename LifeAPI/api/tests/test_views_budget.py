from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils.timezone import now

from api.models import (
    ModuleType,
    UserModule,
    BudgetCategory,
    BudgetPurchase,
    BudgetCashFlow,
    Period
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

    def test_bulk_purchase(self):
        self.client.force_authenticate(user=self.user)
        data = [
            {
                'purchase_date': '2024-02-01',
                'amount': 30.00,
                'description': 'Aldi',
                'category': self.category.id
            },
            {
                'purchase_date': '2024-02-01',
                'amount': 30.00,
                'description': 'Aldi',
                'category': self.category.id
            }
        ]
        response = self.client.post(f'{self.base_url}bulk/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(response.data), 2)

class BudgetPurchaseSummaryViewSetTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='user@example.com', password='password123')
        self.budget_type = ModuleType.objects.get(name='budget')
        self.budget = UserModule.objects.create(user=self.user, module=self.budget_type, name='Test Budget', order=0, is_enabled=True)
        self.category = BudgetCategory.objects.create(user_module=self.budget, name='Food', weekly_target=100, order=0)

        # Purchases in two different ISO weeks
        BudgetPurchase.objects.create(
            user_module=self.budget,
            purchase_date='2025-01-02',
            amount=20.00,
            description='Groceries',
            category=self.category
        )
        BudgetPurchase.objects.create(
            user_module=self.budget,
            purchase_date='2025-01-10',
            amount=30.00,
            description='More groceries',
            category=self.category
        )

        self.base_url = f'/api/budgets/{self.budget.id}/summary/'

    def test_unauthenticated(self):
        response = self.client.get(self.base_url, {'start_date': '2025-01-01', 'end_date': '2025-02-01'})
        self.assertEqual(response.status_code, 401)

    def test_valid_summary_response(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.base_url, {'start_date': '2025-01-01', 'end_date': '2025-02-01'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        weeks = sorted([entry['week'] for entry in response.data])
        self.assertEqual(weeks, [1, 2])

    def test_missing_date_params(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.base_url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('detail', response.data)

    def test_invalid_date_format(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.base_url, {'start_date': '2025-01-01', 'end_date': 'invalid-date'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('detail', response.data)

    def test_no_results_in_range(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.base_url, {'start_date': '2024-01-01', 'end_date': '2024-12-31'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])

class BudgetPurchaseSummaryYearsTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='user@example.com', password='password123')
        self.other_user = User.objects.create_user(email='other@example.com', password='password456')
        self.budget_type = ModuleType.objects.get(name='budget')

        self.budget = UserModule.objects.create(user=self.user, module=self.budget_type, name='My Budget', order=0, is_enabled=True)
        self.other_budget = UserModule.objects.create(user=self.other_user, module=self.budget_type, name='Other Budget', order=1, is_enabled=True)

        self.category = BudgetCategory.objects.create(user_module=self.budget, name='Groceries', weekly_target=100, order=0)

        BudgetPurchase.objects.create(
            user_module=self.budget,
            purchase_date='2022-01-15',
            amount=50,
            description='Old Year',
            category=self.category
        )
        BudgetPurchase.objects.create(
            user_module=self.budget,
            purchase_date=f'{now().year}-04-10',
            amount=75,
            description='This Year',
            category=self.category
        )

        self.url = reverse('budget-summary-list-years', args=[self.budget.id])
        self.other_url = reverse('budget-summary-list-years', args=[self.other_budget.id])

    def test_unauthenticated_user_cannot_access(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_can_see_years_for_own_budget(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        current_year = now().year
        self.assertIn(2022, response.data)
        self.assertIn(current_year, response.data)

    def test_cannot_access_other_users_budget(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.other_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

class BudgetCashFlowViewSetTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='user@example.com', password='password123')
        self.other_user = User.objects.create_user(email='other@example.com', password='password456')
        self.budget_type = ModuleType.objects.get(name='budget')

        self.budget = UserModule.objects.create(user=self.user, module=self.budget_type, name='Main Budget', order=0, is_enabled=True)
        self.other_budget = UserModule.objects.create(user=self.other_user, module=self.budget_type, name='Other Budget', order=1, is_enabled=True)

        self.yearlyPeriod = Period.objects.get(name='yearly')
        self.monthlyPeriod = Period.objects.get(name='monthly')

        self.cashflow1 = BudgetCashFlow.objects.create(
            user_module=self.budget,
            amount=1000,
            description='Annual Salary',
            is_income=True,
            period_id=self.yearlyPeriod.id
        )

        self.cashflow2 = BudgetCashFlow.objects.create(
            user_module=self.other_budget,
            amount=500,
            description='Monthly Rent',
            is_income=False,
            period_id=self.monthlyPeriod.id
        )

        self.base_url = f'/api/budgets/{self.budget.id}/cashflows/'

    def test_unauthenticated_user_cannot_access(self):
        response = self.client.get(self.base_url)
        self.assertEqual(response.status_code, 401)

    def test_list_cashflows(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.base_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['description'], 'Annual Salary')

    def test_retrieve_cashflow(self):
        self.client.force_authenticate(user=self.user)
        url = f'{self.base_url}{self.cashflow1.id}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['amount'], '1000.00')

    def test_create_cashflow(self):
        self.client.force_authenticate(user=self.user)
        data = {
            'amount': 500,
            'description': 'Freelance',
            'is_income': True,
            'period': self.yearlyPeriod.id
        }
        response = self.client.post(self.base_url, data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['description'], 'Freelance')

    def test_update_cashflow(self):
        self.client.force_authenticate(user=self.user)
        url = f'{self.base_url}{self.cashflow1.id}/'
        data = {
            'amount': 1200,
            'description': 'Updated Salary',
            'is_income': True,
            'period': 4
        }
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['amount'], '1200.00')

    def test_delete_cashflow(self):
        self.client.force_authenticate(user=self.user)
        url = f'{self.base_url}{self.cashflow1.id}/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204)
        self.assertFalse(BudgetCashFlow.objects.filter(id=self.cashflow1.id).exists())

    def test_user_cannot_access_other_budget(self):
        self.client.force_authenticate(user=self.user)
        other_url = f'/api/budgets/{self.other_budget.id}/cashflows/'
        response = self.client.get(other_url)
        self.assertEqual(response.status_code, 404)

    def test_user_cannot_access_other_cashflow(self):
        self.client.force_authenticate(user=self.user)
        other_url = f'/api/budgets/{self.budget.id}/cashflows/{self.cashflow2.id}/'
        response = self.client.get(other_url)
        self.assertEqual(response.status_code, 404)

    def test_invalid_period(self):
        self.client.force_authenticate(user=self.user)
        data = {
            'amount': 250,
            'description': 'Invalid Period',
            'is_income': False,
            'period': 9999  # Non-existent
        }
        response = self.client.post(self.base_url, data)
        self.assertEqual(response.status_code, 400)
        self.assertIn('period', response.data)