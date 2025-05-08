from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

from api.models import ModuleType, UserModule

User = get_user_model()

class ModuleTypeViewSetTests(TestCase):
    """Test the Module Type ViewSet functionality"""

    def setUp(self):
        """Set up test data and authenticated client"""
        # Create a test user
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpassword123'
        )

        # Get existing module types from migrations
        self.budget_module_type = ModuleType.objects.get(name='budget')
        self.list_module_type = ModuleType.objects.get(name='list')

        # Set up the API client
        self.client = APIClient()

        # URLs for testing
        self.module_types_url = reverse('moduletype-list')

    def test_module_types_unauthenticated(self):
        """Test that unauthenticated requests are rejected"""
        response = self.client.get(self.module_types_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_module_types_list(self):
        """Test listing all module types"""
        # Authenticate the user
        self.client.force_authenticate(user=self.user)

        # Make the request
        response = self.client.get(self.module_types_url)

        # Check response
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Handle potential pagination
        if 'results' in response.data:
            module_types = response.data['results']
        else:
            module_types = response.data

        # Check that the correct number of module types are returned
        self.assertEqual(len(module_types), 2)  # budget and list

        # Check that the correct module types are returned
        module_type_names = [item['name'] for item in module_types]
        self.assertIn('budget', module_type_names)
        self.assertIn('list', module_type_names)

        # Check that fields are correct
        for module_type in module_types:
            self.assertIn('id', module_type)
            self.assertIn('name', module_type)

    def test_module_type_detail(self):
        """Test retrieving a single module type"""
        # Authenticate the user
        self.client.force_authenticate(user=self.user)

        # Get the detail URL
        detail_url = reverse('moduletype-detail', args=[self.list_module_type.id])

        # Make the request
        response = self.client.get(detail_url)

        # Check response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'list')

    def test_module_type_create_not_allowed(self):
        """Test that POST requests are not allowed (read-only viewset)"""
        # Authenticate the user
        self.client.force_authenticate(user=self.user)

        # Attempt to create a new module type
        new_module_type = {
            'name': 'calendar'
        }
        response = self.client.post(self.module_types_url, new_module_type, format='json')

        # Check that the request is rejected
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_module_type_update_not_allowed(self):
        """Test that PUT requests are not allowed (read-only viewset)"""
        # Authenticate the user
        self.client.force_authenticate(user=self.user)

        # Get the detail URL
        detail_url = reverse('moduletype-detail', args=[self.list_module_type.id])

        # Attempt to update the module type
        updated_data = {
            'name': 'updated_list'
        }
        response = self.client.put(detail_url, updated_data, format='json')

        # Check that the request is rejected
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_module_type_delete_not_allowed(self):
        """Test that DELETE requests are not allowed (read-only viewset)"""
        # Authenticate the user
        self.client.force_authenticate(user=self.user)

        # Get the detail URL
        detail_url = reverse('moduletype-detail', args=[self.list_module_type.id])

        # Attempt to delete the module type
        response = self.client.delete(detail_url)

        # Check that the request is rejected
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class UserModuleViewSetTests(TestCase):
    """Test the User Module ViewSet functionality"""

    def setUp(self):
        """Set up test data and authenticated client"""
        # Create test users
        self.user1 = User.objects.create_user(
            email='user1@example.com',
            password='password123'
        )
        self.user2 = User.objects.create_user(
            email='user2@example.com',
            password='password123'
        )

        # Get existing module types from migrations
        self.list_module_type = ModuleType.objects.get(name='list')
        self.budget_module_type = ModuleType.objects.get(name='budget')

        # Create user modules for testing
        self.user1_list = UserModule.objects.create(
            user=self.user1,
            module=self.list_module_type,
            name='My Tasks',
            order=1,
            is_enabled=True
        )
        self.user1_budget = UserModule.objects.create(
            user=self.user1,
            module=self.budget_module_type,
            name='My Budget',
            order=2,
            is_enabled=True
        )
        self.user2_list = UserModule.objects.create(
            user=self.user2,
            module=self.list_module_type,
            name='User2 Tasks',
            order=1,
            is_enabled=True
        )

        # Set up the API client
        self.client = APIClient()

        # URLs for testing
        self.user_modules_url = reverse('user-module-list')

    def test_user_modules_unauthenticated(self):
        """Test that unauthenticated requests are rejected"""
        response = self.client.get(self.user_modules_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_user_modules(self):
        """Test that a user can get their own modules but not others'"""
        # Authenticate as user1
        self.client.force_authenticate(user=self.user1)

        # Make the request
        response = self.client.get(self.user_modules_url)

        # Check response
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Handle potential pagination
        if 'results' in response.data:
            modules = response.data['results']
        else:
            modules = response.data

        # Check that only user1's modules are returned
        self.assertEqual(len(modules), 2)  # user1 has 2 modules
        module_names = [module['name'] for module in modules]
        self.assertIn('My Tasks', module_names)
        self.assertIn('My Budget', module_names)
        self.assertNotIn('User2 Tasks', module_names)

        # Now authenticate as user2
        self.client.force_authenticate(user=self.user2)

        # Make the request
        response = self.client.get(self.user_modules_url)

        # Check response
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Handle potential pagination
        if 'results' in response.data:
            modules = response.data['results']
        else:
            modules = response.data

        # Check that only user2's modules are returned
        self.assertEqual(len(modules), 1)  # user2 has 1 module
        self.assertEqual(modules[0]['name'], 'User2 Tasks')

    def test_create_user_module(self):
        """Test creating a new user module"""
        # Authenticate as user1
        self.client.force_authenticate(user=self.user1)

        # Data for a new module
        new_module_data = {
            'module': self.list_module_type.id,
            'name': 'Shopping List',
            'order': 3,
            'is_enabled': True,
            'is_read_only': False,
            'is_checkable': True
        }

        # Make the request
        response = self.client.post(self.user_modules_url, new_module_data, format='json')

        # Check response
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Shopping List')
        self.assertEqual(response.data['order'], 3)
        self.assertTrue(response.data['is_enabled'])
        self.assertFalse(response.data['is_read_only'])
        self.assertTrue(response.data['is_checkable'])

        # Check that the module was actually created in the database
        self.assertTrue(UserModule.objects.filter(
            user=self.user1,
            name='Shopping List',
            order=3
        ).exists())

    def test_update_user_module(self):
        """Test updating an existing user module"""
        # Authenticate as user1
        self.client.force_authenticate(user=self.user1)

        # Get the detail URL
        detail_url = reverse('user-module-detail', args=[self.user1_list.id])

        # Data for updating the module
        update_data = {
            'name': 'Updated Tasks',
            'is_enabled': False
        }

        # Make the request
        response = self.client.patch(detail_url, update_data, format='json')

        # Check response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Updated Tasks')
        self.assertFalse(response.data['is_enabled'])

        # Check that the module was actually updated in the database
        self.user1_list.refresh_from_db()
        self.assertEqual(self.user1_list.name, 'Updated Tasks')
        self.assertFalse(self.user1_list.is_enabled)

    def test_delete_user_module(self):
        """Test deleting a user module"""
        # Authenticate as user1
        self.client.force_authenticate(user=self.user1)

        # Get the detail URL
        detail_url = reverse('user-module-detail', args=[self.user1_list.id])

        # Make the request
        response = self.client.delete(detail_url)

        # Check response
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Check that the module was actually deleted from the database
        self.assertFalse(UserModule.objects.filter(id=self.user1_list.id).exists())

    def test_cannot_access_other_users_module(self):
        """Test that a user cannot access another user's modules"""
        # Authenticate as user1
        self.client.force_authenticate(user=self.user1)

        # Get the detail URL for user2's module
        detail_url = reverse('user-module-detail', args=[self.user2_list.id])

        # Make the request
        response = self.client.get(detail_url)

        # Check response - should be 404 since queryset is filtered by user
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # Try to update the module
        update_data = {
            'name': 'Hacked Module'
        }
        response = self.client.patch(detail_url, update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # Try to delete the module
        response = self.client.delete(detail_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # Check that user2's module still exists
        self.assertTrue(UserModule.objects.filter(id=self.user2_list.id).exists())