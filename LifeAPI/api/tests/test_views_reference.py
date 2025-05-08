from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

from api.models import FieldType, FieldTypeRule, ModuleType

User = get_user_model()

class FieldTypeViewSetTests(TestCase):
    """Test the Field Type ViewSet functionality"""

    def setUp(self):
        """Set up test data and authenticated client"""
        # Create a test user
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpassword123'
        )

        # Get existing field types from database
        self.text_type = FieldType.objects.get(name='text')
        self.number_type = FieldType.objects.get(name='number')
        self.date_type = FieldType.objects.get(name='date')
        self.dropdown_type = FieldType.objects.get(name='dropdown')

        # Get existing module types
        self.budget_module_type = ModuleType.objects.get(name='budget')
        self.list_module_type = ModuleType.objects.get(name='list')

        # Get existing field type rules
        # For text type
        self.text_rule1 = FieldTypeRule.objects.get(field_type=self.text_type, rule='email')
        self.text_rule2 = FieldTypeRule.objects.get(field_type=self.text_type, rule='mobile')

        # For number type
        self.number_rule1 = FieldTypeRule.objects.get(field_type=self.number_type, rule='positive_only')
        self.number_rule2 = FieldTypeRule.objects.get(field_type=self.number_type, rule='integer')
        self.number_rule3 = FieldTypeRule.objects.get(field_type=self.number_type, rule='money')

        # Set up the API client
        self.client = APIClient()

        # URLs for testing
        self.field_types_url = reverse('field-type-list')

    def test_field_types_unauthenticated(self):
        """Test that unauthenticated requests are rejected"""
        response = self.client.get(self.field_types_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_field_types_list(self):
        """Test listing all field types (non-paginated)"""
        self.client.force_authenticate(user=self.user)

        response = self.client.get(self.field_types_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Response should be a plain list
        self.assertIsInstance(response.data, list)
        self.assertEqual(len(response.data), 4)

        # Check that all expected field types are present
        field_type_names = [ft['name'] for ft in response.data]
        self.assertIn('text', field_type_names)
        self.assertIn('number', field_type_names)
        self.assertIn('date', field_type_names)
        self.assertIn('dropdown', field_type_names)

        for field_type in response.data:
            self.assertIn('id', field_type)
            self.assertIn('name', field_type)
            self.assertNotIn('rules', field_type)

    def test_field_type_detail(self):
        """Test retrieving a single field type with its rules"""
        # Authenticate the user
        self.client.force_authenticate(user=self.user)

        # Get the detail URL
        detail_url = reverse('field-type-detail', args=[self.text_type.id])

        # Make the request
        response = self.client.get(detail_url)

        # Check response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'text')

        # Check that rules are included
        self.assertIn('rules', response.data)
        self.assertEqual(len(response.data['rules']), 2)  # Two rules for text type

        # Check rule contents with the actual rules from your data
        rule_values = [rule['rule'] for rule in response.data['rules']]
        self.assertIn('email', rule_values)
        self.assertIn('mobile', rule_values)

    def test_field_type_detail_with_query_param(self):
        """Test retrieving field types with detailed=true returns full list with rules"""
        self.client.force_authenticate(user=self.user)

        response = self.client.get(f"{self.field_types_url}?detailed=true")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertIsInstance(response.data, list)
        self.assertEqual(len(response.data), 4)

        for field_type in response.data:
            self.assertIn('rules', field_type)

            if field_type['name'] == 'text':
                self.assertEqual(len(field_type['rules']), 2)
                rule_values = [rule['rule'] for rule in field_type['rules']]
                self.assertIn('email', rule_values)
                self.assertIn('mobile', rule_values)

            elif field_type['name'] == 'number':
                self.assertEqual(len(field_type['rules']), 3)
                rule_values = [rule['rule'] for rule in field_type['rules']]
                self.assertIn('positive_only', rule_values)
                self.assertIn('integer', rule_values)
                self.assertIn('money', rule_values)

            elif field_type['name'] in ['date', 'dropdown']:
                self.assertEqual(len(field_type['rules']), 0)

    def test_field_type_create_not_allowed(self):
        """Test that POST requests are not allowed (read-only viewset)"""
        # Authenticate the user
        self.client.force_authenticate(user=self.user)

        # Attempt to create a new field type
        new_field_type = {
            'name': 'new_field_type'
        }
        response = self.client.post(self.field_types_url, new_field_type, format='json')

        # Check that the request is rejected
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_field_type_update_not_allowed(self):
        """Test that PUT requests are not allowed (read-only viewset)"""
        # Authenticate the user
        self.client.force_authenticate(user=self.user)

        # Get the detail URL
        detail_url = reverse('field-type-detail', args=[self.text_type.id])

        # Attempt to update the field type
        updated_data = {
            'name': 'updated_text'
        }
        response = self.client.put(detail_url, updated_data, format='json')

        # Check that the request is rejected
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_field_type_delete_not_allowed(self):
        """Test that DELETE requests are not allowed (read-only viewset)"""
        # Authenticate the user
        self.client.force_authenticate(user=self.user)

        # Get the detail URL
        detail_url = reverse('field-type-detail', args=[self.text_type.id])

        # Attempt to delete the field type
        response = self.client.delete(detail_url)

        # Check that the request is rejected
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)