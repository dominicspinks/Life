from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status

from api.models import (
    ModuleType,
    UserModule,
    FieldType,
    ListField,
    ListFieldRule,
    ListFieldOption,
    ListItem,
    FieldTypeRule
)

User = get_user_model()

class ListConfigurationViewSetTests(APITestCase):
    """Test the List Configuration ViewSet functionality"""

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

        # Get existing module and field types from migrations
        self.list_module_type = ModuleType.objects.get(name='list')
        self.text_field_type = FieldType.objects.get(name='text')
        self.number_field_type = FieldType.objects.get(name='number')
        self.dropdown_field_type = FieldType.objects.get(name='dropdown')

        # Create user modules for testing
        self.user1_list = UserModule.objects.create(
            user=self.user1,
            module=self.list_module_type,
            name='My Tasks',
            order=1,
            is_enabled=True
        )
        self.user2_list = UserModule.objects.create(
            user=self.user2,
            module=self.list_module_type,
            name='User2 Tasks',
            order=1,
            is_enabled=True
        )

        # Create list fields for user1's list
        self.task_name_field = ListField.objects.create(
            user_module=self.user1_list,
            field_type=self.text_field_type,
            field_name='Task Name',
            is_mandatory=True,
            order=0
        )
        self.priority_field = ListField.objects.create(
            user_module=self.user1_list,
            field_type=self.dropdown_field_type,
            field_name='Priority',
            is_mandatory=False,
            order=1
        )

        # Create dropdown options for the priority field
        self.option_high = ListFieldOption.objects.create(
            list_field=self.priority_field,
            option_name='High'
        )
        self.option_medium = ListFieldOption.objects.create(
            list_field=self.priority_field,
            option_name='Medium'
        )
        self.option_low = ListFieldOption.objects.create(
            list_field=self.priority_field,
            option_name='Low'
        )

        # URLs for testing
        self.list_configuration_url = reverse('configuration-list')

    def test_list_configurations_unauthenticated(self):
        """Test that unauthenticated requests are rejected"""
        response = self.client.get(self.list_configuration_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_list_configurations(self):
        """Test retrieving list configurations"""
        # Authenticate as user1
        self.client.force_authenticate(user=self.user1)

        # Make the request
        response = self.client.get(self.list_configuration_url)

        # Check response
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Handle potential pagination
        if 'results' in response.data:
            configs = response.data['results']
        else:
            configs = response.data

        # Check that only user1's list configurations are returned
        self.assertEqual(len(configs), 1)
        self.assertEqual(configs[0]['name'], 'My Tasks')

        # Check that fields data is included
        self.assertEqual(len(configs[0]['list_fields']), 2)
        field_names = [field['field_name'] for field in configs[0]['list_fields']]
        self.assertIn('Task Name', field_names)
        self.assertIn('Priority', field_names)

        # Check that the dropdown options are included
        priority_field = next(field for field in configs[0]['list_fields'] if field['field_name'] == 'Priority')
        self.assertEqual(len(priority_field['options']), 3)
        option_names = [option['option_name'] for option in priority_field['options']]
        self.assertIn('High', option_names)
        self.assertIn('Medium', option_names)
        self.assertIn('Low', option_names)

    def test_get_list_configuration_detail(self):
        """Test retrieving a specific list configuration"""
        # Authenticate as user1
        self.client.force_authenticate(user=self.user1)

        # Get the detail URL
        detail_url = reverse('configuration-detail', args=[self.user1_list.id])

        # Make the request
        response = self.client.get(detail_url)

        # Check response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'My Tasks')
        self.assertEqual(len(response.data['list_fields']), 2)

    def test_cannot_create_list_configuration(self):
        """Test that list configuration creation is not allowed"""
        # Authenticate as user1
        self.client.force_authenticate(user=self.user1)

        # Data for a new list configuration
        new_config_data = {
            'name': 'New List',
            'module': self.list_module_type.id,
            'order': 2,
            'is_enabled': True
        }

        # Make the request
        response = self.client.post(self.list_configuration_url, new_config_data, format='json')

        # Check response - should be 405 Method Not Allowed
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_cannot_delete_list_configuration(self):
        """Test that list configuration deletion is not allowed"""
        # Authenticate as user1
        self.client.force_authenticate(user=self.user1)

        # Get the detail URL
        detail_url = reverse('configuration-detail', args=[self.user1_list.id])

        # Make the request
        response = self.client.delete(detail_url)

        # Check response - should be 405 Method Not Allowed
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_list_configuration(self):
        """Test updating a list configuration"""
        # Authenticate as user1
        self.client.force_authenticate(user=self.user1)

        # Get the detail URL
        detail_url = reverse('configuration-detail', args=[self.user1_list.id])

        # Data for updating the list configuration
        update_data = {
            'name': 'Updated Tasks',
            'module': self.list_module_type.id,
            'order': self.user1_list.order,
            'is_enabled': False,
            'list_fields': [
                # Keep existing task name field
                {
                    'id': self.task_name_field.id,
                    'field_name': 'Task Name',
                    'field_type': self.text_field_type.id,
                    'is_mandatory': True,
                    'order': 0
                },
                # Keep existing priority field
                {
                    'id': self.priority_field.id,
                    'field_name': 'Priority Level',  # Updated name
                    'field_type': self.dropdown_field_type.id,
                    'is_mandatory': True,  # Updated to mandatory
                    'order': 1,
                    'options': [
                        {'option_name': 'High'},
                        {'option_name': 'Medium'},
                        {'option_name': 'Low'},
                        {'option_name': 'Critical'}  # Added new option
                    ]
                },
                # Add a new field
                {
                    'field_name': 'Due Date',
                    'field_type': self.text_field_type.id,
                    'is_mandatory': False,
                    'order': 2
                }
            ]
        }

        # Make the request
        response = self.client.put(detail_url, update_data, format='json')

        # Check response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Updated Tasks')
        self.assertFalse(response.data['is_enabled'])

        # Check that the fields were updated
        self.assertEqual(len(response.data['list_fields']), 3)  # Now 3 fields

        # Check that the Priority field was updated
        priority_field = next(field for field in response.data['list_fields'] if field['field_name'] == 'Priority Level')
        self.assertTrue(priority_field['is_mandatory'])
        self.assertEqual(len(priority_field['options']), 4)  # Now 4 options
        option_names = [option['option_name'] for option in priority_field['options']]
        self.assertIn('Critical', option_names)

        # Check that the new field was added
        self.assertTrue(any(field['field_name'] == 'Due Date' for field in response.data['list_fields']))

        # Check that the database was updated
        self.user1_list.refresh_from_db()
        self.assertEqual(self.user1_list.name, 'Updated Tasks')
        self.assertFalse(self.user1_list.is_enabled)

        # Check list fields
        list_fields = ListField.objects.filter(user_module=self.user1_list)
        self.assertEqual(list_fields.count(), 3)

        # Check priority field options
        priority_field = ListField.objects.get(user_module=self.user1_list, field_name='Priority Level')
        options = ListFieldOption.objects.filter(list_field=priority_field)
        self.assertEqual(options.count(), 4)
        self.assertTrue(options.filter(option_name='Critical').exists())

    def test_update_list_configuration_remove_field(self):
        """Test updating a list configuration by removing a field"""
        # Authenticate as user1
        self.client.force_authenticate(user=self.user1)

        # Get the detail URL
        detail_url = reverse('configuration-detail', args=[self.user1_list.id])

        # Data for updating the list configuration - removing the priority field
        update_data = {
        'name': 'Tasks',
        'module': self.list_module_type.id,
        'order': self.user1_list.order,
        'is_enabled': True,
        'list_fields': [
            # Keep only the task name field
            {
                'id': self.task_name_field.id,
                'field_name': 'Task Name',
                'field_type': self.text_field_type.id,
                'is_mandatory': True,
                'order': 0
            }
        ]
    }

        # Make the request
        response = self.client.put(detail_url, update_data, format='json')

        # Check response
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check that only one field remains
        self.assertEqual(len(response.data['list_fields']), 1)
        self.assertEqual(response.data['list_fields'][0]['field_name'], 'Task Name')

        # Check that the database was updated
        list_fields = ListField.objects.filter(user_module=self.user1_list)
        self.assertEqual(list_fields.count(), 1)
        self.assertEqual(list_fields[0].field_name, 'Task Name')

        # Check that the priority field and its options were deleted
        self.assertFalse(ListField.objects.filter(id=self.priority_field.id).exists())
        self.assertEqual(ListFieldOption.objects.filter(list_field=self.priority_field).count(), 0)

    def test_cannot_access_other_users_list_configuration(self):
        """Test that a user cannot access another user's list configuration"""
        # Authenticate as user1
        self.client.force_authenticate(user=self.user1)

        # Get the detail URL for user2's list
        detail_url = reverse('configuration-detail', args=[self.user2_list.id])

        # Make the request
        response = self.client.get(detail_url)

        # Check response - should be 404 since queryset is filtered by user
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_list_configurations_with_get_all(self):
        """Test retrieving list configurations with get_all=true returns raw list"""
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(self.list_configuration_url, {'get_all': 'true'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # It should return a list, not a paginated dict
        self.assertIsInstance(response.data, list)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'My Tasks')

class ListConfigurationFieldViewSetTests(APITestCase):
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

        # Get existing types from migration
        self.module_type = ModuleType.objects.get(name='list')
        self.number_field_type = FieldType.objects.get(name='number')
        self.number_field_rule = FieldTypeRule.objects.get(field_type=self.number_field_type, rule='integer')

        # Create module and field
        self.user1_module = UserModule.objects.create(
            user=self.user1,
            module=self.module_type,
            name='My List',
            order=1,
            is_enabled=True
        )

        self.user1_list_field = ListField.objects.create(
            user_module=self.user1_module,
            field_type=self.number_field_type,
            field_name='Amount',
            is_mandatory=True,
            order=1
        )

        # Add associated rule
        ListFieldRule.objects.create(list_field=self.user1_list_field, field_type_rule=self.number_field_rule)

        self.user2_module = UserModule.objects.create(
            user=self.user2,
            module=self.module_type,
            name='User2 List',
            order=1,
            is_enabled=True
        )

        self.user2_list_field = ListField.objects.create(
            user_module=self.user2_module,
            field_type=self.number_field_type,
            field_name='Other Field',
            is_mandatory=True,
            order=1
        )

        # Add associated rule
        ListFieldRule.objects.create(list_field=self.user2_list_field, field_type_rule=self.number_field_rule)

        self.detail_url = reverse('configuration-fields-detail', args=[self.user1_module.id, self.user1_list_field.id])

    def test_list_configurations_unauthenticated(self):
        """Test that unauthenticated requests are rejected"""
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_field_detail(self):
        # Authenticate as user1
        self.client.force_authenticate(user=self.user1)

        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['field_name'], 'Amount')

    def test_update_field_and_rules(self):
        # Authenticate as user1
        self.client.force_authenticate(user=self.user1)

        update_data = {
            'user_module': self.user1_module.id,
            'field_name': 'Total Cost',
            'field_type': self.number_field_type.id,
            'is_mandatory': False,
            'order': 1,
            'rules': [
                {'field_type_rule': self.number_field_rule.id}
            ]
        }
        response = self.client.put(self.detail_url, update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['field_name'], 'Total Cost')

    def test_patch_field_name_only(self):
        # Authenticate as user1
        self.client.force_authenticate(user=self.user1)

        response = self.client.patch(self.detail_url, {'field_name': 'Updated Name'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['field_name'], 'Updated Name')

    def test_delete_field(self):
        # Authenticate as user1
        self.client.force_authenticate(user=self.user1)

        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(ListField.objects.filter(id=self.user1_list_field.id).exists())
        self.assertEqual(ListFieldRule.objects.filter(list_field=self.user1_list_field).count(), 0)

    def test_cannot_access_other_users_field(self):
        # Authenticate as user1
        self.client.force_authenticate(user=self.user1)

        url = reverse('configuration-fields-detail', args=[self.user2_module.id,self.user2_list_field.id])

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        response = self.client.patch(url, {'field_name': 'Hack'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

class ListDataViewSetTests(APITestCase):
    """Test the List Data ViewSet functionality"""

    def setUp(self):
        """Set up test data and authenticated client"""
        # Create test user
        self.user = User.objects.create_user(
            email='user@example.com',
            password='password123'
        )

        # Get existing module and field types from migrations
        self.list_module_type = ModuleType.objects.get(name='list')
        self.text_field_type = FieldType.objects.get(name='text')

        # Create user module for testing
        self.user_list = UserModule.objects.create(
            user=self.user,
            module=self.list_module_type,
            name='My Tasks',
            order=1,
            is_enabled=True
        )

        # Create list fields
        self.task_name_field = ListField.objects.create(
            user_module=self.user_list,
            field_type=self.text_field_type,
            field_name='Task Name',
            is_mandatory=True,
            order=0
        )

        # Create list items
        self.list_item1 = ListItem.objects.create(
            user_module=self.user_list,
            is_completed=False,
            fields=[{'field': self.task_name_field.id, 'value': 'Task 1'}]
        )
        self.list_item2 = ListItem.objects.create(
            user_module=self.user_list,
            is_completed=True,
            fields=[{'field': self.task_name_field.id, 'value': 'Task 2'}]
        )

        # URLs for testing
        self.list_data_url = reverse('data-list')

    def test_list_data_unauthenticated(self):
        """Test that unauthenticated requests are rejected"""
        response = self.client.get(self.list_data_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_list_data(self):
        """Test retrieving list data with items"""
        # Authenticate as user
        self.client.force_authenticate(user=self.user)

        # Make the request
        response = self.client.get(self.list_data_url)

        # Check response
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Handle potential pagination
        if 'results' in response.data:
            data_lists = response.data['results']
        else:
            data_lists = response.data

        # Check that the list data is returned
        self.assertEqual(len(data_lists), 1)
        list_data = data_lists[0]
        self.assertEqual(list_data['name'], 'My Tasks')

        # Check that fields data is included
        self.assertEqual(len(list_data['list_fields']), 1)
        self.assertEqual(list_data['list_fields'][0]['field_name'], 'Task Name')

        # Check that items data is included
        self.assertEqual(len(list_data['list_items']), 2)

        # Check item details
        item_values = [item['field_values'][0]['value'] for item in list_data['list_items']]
        self.assertIn('Task 1', item_values)
        self.assertIn('Task 2', item_values)

        # Check completed status
        completed_items = [item for item in list_data['list_items'] if item['is_completed']]
        self.assertEqual(len(completed_items), 1)
        self.assertEqual(completed_items[0]['field_values'][0]['value'], 'Task 2')

    def test_get_list_data_detail(self):
        """Test retrieving a specific list's data"""
        # Authenticate as user
        self.client.force_authenticate(user=self.user)

        # Get the detail URL
        detail_url = reverse('data-detail', args=[self.user_list.id])

        # Make the request
        response = self.client.get(detail_url)

        # Check response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'My Tasks')
        self.assertEqual(len(response.data['list_fields']), 1)
        self.assertEqual(len(response.data['list_items']), 2)

    def test_get_list_data_with_get_all(self):
        """Test retrieving list data with get_all=true returns raw list"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.list_data_url, {'get_all': 'true'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'My Tasks')

class ListItemViewSetTests(APITestCase):
    """Test the List Item ViewSet functionality"""

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

        # Get existing module and field types from migrations
        self.list_module_type = ModuleType.objects.get(name='list')
        self.text_field_type = FieldType.objects.get(name='text')
        self.number_field_type = FieldType.objects.get(name='number')
        self.dropdown_field_type = FieldType.objects.get(name='dropdown')

        # Create user modules for testing
        self.user1_list = UserModule.objects.create(
            user=self.user1,
            module=self.list_module_type,
            name='My Tasks',
            order=1,
            is_enabled=True
        )
        self.user2_list = UserModule.objects.create(
            user=self.user2,
            module=self.list_module_type,
            name='User2 Tasks',
            order=1,
            is_enabled=True
        )

        # Create list fields for user1's list
        self.task_name_field = ListField.objects.create(
            user_module=self.user1_list,
            field_type=self.text_field_type,
            field_name='Task Name',
            is_mandatory=True,
            order=0
        )
        self.priority_field = ListField.objects.create(
            user_module=self.user1_list,
            field_type=self.dropdown_field_type,
            field_name='Priority',
            is_mandatory=False,
            order=1
        )

        # Create dropdown options for the priority field
        self.option_high = ListFieldOption.objects.create(
            list_field=self.priority_field,
            option_name='High'
        )
        self.option_medium = ListFieldOption.objects.create(
            list_field=self.priority_field,
            option_name='Medium'
        )
        self.option_low = ListFieldOption.objects.create(
            list_field=self.priority_field,
            option_name='Low'
        )

        # Create list items
        self.list_item1 = ListItem.objects.create(
            user_module=self.user1_list,
            is_completed=False,
            fields=[
                {'field': self.task_name_field.id, 'value': 'Task 1'},
                {'field': self.priority_field.id, 'value': 'High'}
            ]
        )

        # URLs for testing
        self.list_items_url = reverse('list-items-list', args=[self.user1_list.id])
        self.list_item_detail_url = reverse('list-items-detail', args=[self.user1_list.id, self.list_item1.id])

    def test_list_items_unauthenticated(self):
        """Test that unauthenticated requests are rejected"""
        response = self.client.get(self.list_items_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_list_items(self):
        """Test retrieving items for a list"""
        # Authenticate as user1
        self.client.force_authenticate(user=self.user1)

        # Make the request
        response = self.client.get(self.list_items_url)

        # Check response
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Handle potential pagination
        if 'results' in response.data:
            items = response.data['results']
        else:
            items = response.data

        # Check that the correct items are returned
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]['id'], self.list_item1.id)
        self.assertFalse(items[0]['is_completed'])

        # Check field values
        self.assertEqual(len(items[0]['field_values']), 2)
        field_values = {field['field']: field['value'] for field in items[0]['field_values']}
        self.assertEqual(field_values[self.task_name_field.id], 'Task 1')
        self.assertEqual(field_values[self.priority_field.id], 'High')

    def test_create_list_item(self):
        """Test creating a new list item"""
        # Authenticate as user1
        self.client.force_authenticate(user=self.user1)

        # Data for a new list item
        new_item_data = {
            'is_completed': False,
            'field_values': [
                {'field': self.task_name_field.id, 'value': 'New Task'},
                {'field': self.priority_field.id, 'value': 'Medium'}
            ]
        }

        # Make the request
        response = self.client.post(self.list_items_url, new_item_data, format='json')

        # Check response
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertFalse(response.data['is_completed'])

        # Check field values in response
        field_values_response = {item['field']: item['value'] for item in response.data['field_values']}
        self.assertEqual(field_values_response[self.task_name_field.id], 'New Task')
        self.assertEqual(field_values_response[self.priority_field.id], 'Medium')

        # Check that the item was actually created in the database
        new_item_id = response.data['id']
        self.assertTrue(ListItem.objects.filter(id=new_item_id).exists())
        new_item = ListItem.objects.get(id=new_item_id)
        self.assertEqual(new_item.user_module, self.user1_list)
        self.assertFalse(new_item.is_completed)

        # The field values in the database - convert the field IDs to integers if needed
        field_values_db = {}
        for field_entry in new_item.fields:
            field_id = field_entry['field']
            # Convert to integer if it's stored as a string
            if isinstance(field_id, str):
                field_id = int(field_id)
            field_values_db[field_id] = field_entry['value']

        # Now check the values using integer keys
        self.assertEqual(field_values_db[self.task_name_field.id], 'New Task')
        self.assertEqual(field_values_db[self.priority_field.id], 'Medium')

    def test_update_list_item(self):
        """Test updating an existing list item"""
        # Authenticate as user1
        self.client.force_authenticate(user=self.user1)

        # Data for updating the list item
        update_data = {
            'is_completed': True,
            'field_values': [
                {'field': self.task_name_field.id, 'value': 'Updated Task'},
                {'field': self.priority_field.id, 'value': 'Low'}
            ]
        }

        # Make the request
        response = self.client.put(self.list_item_detail_url, update_data, format='json')

        # Check response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['is_completed'])

        # Check field values
        field_values = {field['field']: field['value'] for field in response.data['field_values']}
        self.assertEqual(field_values[self.task_name_field.id], 'Updated Task')
        self.assertEqual(field_values[self.priority_field.id], 'Low')

        # Check that the item was actually updated in the database
        self.list_item1.refresh_from_db()
        self.assertTrue(self.list_item1.is_completed)

        # Check field values in the database
        field_values_db = {int(field['field']): field['value'] for field in self.list_item1.fields}
        self.assertEqual(field_values_db[self.task_name_field.id], 'Updated Task')
        self.assertEqual(field_values_db[self.priority_field.id], 'Low')

    def test_partial_update_list_item(self):
        """Test partially updating a list item"""
        # Authenticate as user1
        self.client.force_authenticate(user=self.user1)

        # Data for partially updating the list item
        update_data = {
            'is_completed': True
        }

        # Make the request
        response = self.client.patch(self.list_item_detail_url, update_data, format='json')

        # Check response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['is_completed'])

        # Check that the item was actually updated in the database
        self.list_item1.refresh_from_db()
        self.assertTrue(self.list_item1.is_completed)

        # Field values should remain unchanged
        field_values_db = {int(field['field']): field['value'] for field in self.list_item1.fields}
        self.assertEqual(field_values_db[self.task_name_field.id], 'Task 1')
        self.assertEqual(field_values_db[self.priority_field.id], 'High')

    def test_delete_list_item(self):
        """Test deleting a list item"""
        # Authenticate as user1
        self.client.force_authenticate(user=self.user1)

        # Make the request
        response = self.client.delete(self.list_item_detail_url)

        # Check response
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Check that the item was actually deleted from the database
        self.assertFalse(ListItem.objects.filter(id=self.list_item1.id).exists())

    def test_validation_missing_required_field(self):
        """Test validation when a required field is missing"""
        # Authenticate as user1
        self.client.force_authenticate(user=self.user1)

        # Data missing the required task name field
        invalid_data = {
            'is_completed': False,
            'field_values': [
                {'field': self.priority_field.id, 'value': 'Medium'}
            ]
        }

        # Make the request
        response = self.client.post(self.list_items_url, invalid_data, format='json')

        # Check response - should be 400 Bad Request
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('field_values', response.data)
        self.assertIn('Missing required fields', str(response.data))

    def test_validation_invalid_option(self):
        """Test validation when an invalid dropdown option is provided"""
        # Authenticate as user1
        self.client.force_authenticate(user=self.user1)

        # Data with an invalid priority option
        invalid_data = {
            'is_completed': False,
            'field_values': [
                {'field': self.task_name_field.id, 'value': 'New Task'},
                {'field': self.priority_field.id, 'value': 'Invalid Option'}
            ]
        }

        # Make the request
        response = self.client.post(self.list_items_url, invalid_data, format='json')

        # Check response - should be 400 Bad Request
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('field_values', response.data)
        self.assertIn('is not a valid option', str(response.data))

    def test_cannot_access_other_users_list_items(self):
        """Test that a user cannot access another user's list items"""
        # Authenticate as user2
        self.client.force_authenticate(user=self.user2)

        # Try to access user1's list items
        response = self.client.get(self.list_items_url)

        # Check response - should be 404 since queryset is filtered by user
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # Try to access a specific item
        response = self.client.get(self.list_item_detail_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # Try to update an item
        update_data = {
            'is_completed': True
        }
        response = self.client.patch(self.list_item_detail_url, update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # Try to delete an item
        response = self.client.delete(self.list_item_detail_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_list_items_with_get_all(self):
        """Test retrieving list items with get_all=true returns raw list"""
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(self.list_items_url, {'get_all': 'true'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], self.list_item1.id)