from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.exceptions import ValidationError
from api.models import (
    ModuleType,
    UserModule,
    FieldType,
    FieldTypeRule,
    ListField,
    ListFieldRule,
    ListFieldOption,
    ListItem,
    BudgetCategory,
    BudgetPurchase
)
from api.serializers.serializers_auth import EmailTokenObtainSerializer, RegisterSerializer
from api.serializers.serializers_budgets import BudgetCategorySerializer, BudgetPurchaseSerializer, BudgetSerializer
from api.serializers.serializers_lists import ListConfigurationSerializer, ListDataSerializer, ListFieldSerializer, ListItemSerializer
from api.serializers.serializers_modules import ModuleTypeSerializer, UserModuleSerializer
from api.serializers.serializers_reference import FieldTypeDetailSerializer, FieldTypeSerializer

User = get_user_model()

class RegisterSerializerTests(TestCase):
    def test_create_user(self):
        serializer = RegisterSerializer(data={
            'email': 'new@example.com',
            'password': 'StrongPassword123!'
        })
        self.assertTrue(serializer.is_valid())
        user = serializer.save()
        self.assertEqual(user.email, 'new@example.com')
        self.assertTrue(user.check_password('StrongPassword123!'))

    def test_password_validation(self):
        # Test with a weak password
        serializer = RegisterSerializer(data={
            'email': 'new@example.com',
            'password': '123'  # Too short
        })
        self.assertFalse(serializer.is_valid())
        self.assertIn('password', serializer.errors)

class EmailTokenObtainSerializerTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='StrongPassword123!'
        )
        self.valid_data = {
            'email': 'test@example.com',
            'password': 'StrongPassword123!'
        }
        self.invalid_data = {
            'email': 'test@example.com',
            'password': 'wrongpassword'
        }

    def test_valid_credentials(self):
        serializer = EmailTokenObtainSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid())
        validated_data = serializer.validated_data
        self.assertIn('refresh', validated_data)
        self.assertIn('access', validated_data)
        self.assertIn('user', validated_data)
        self.assertEqual(validated_data['user']['email'], 'test@example.com')

    def test_invalid_credentials(self):
        serializer = EmailTokenObtainSerializer(data=self.invalid_data)
        with self.assertRaises(ValidationError):
            serializer.is_valid(raise_exception=True)

    def test_nonexistent_user(self):
        data = {
            'email': 'nonexistent@example.com',
            'password': 'password123'
        }
        serializer = EmailTokenObtainSerializer(data=data)
        with self.assertRaises(ValidationError):
            serializer.is_valid(raise_exception=True)

class FieldTypeSerializerTests(TestCase):
    def setUp(self):
        self.field_type = FieldType.objects.get(name='text')
        self.rule1 = FieldTypeRule.objects.get(field_type=self.field_type, rule='email')
        self.rule2 = FieldTypeRule.objects.get(field_type=self.field_type, rule='mobile')

    def test_field_type_serialization(self):
        serializer = FieldTypeSerializer(self.field_type)
        data = serializer.data
        self.assertEqual(data['id'], self.field_type.id)
        self.assertEqual(data['name'], 'text')

    def test_field_type_detail_serialization(self):
        serializer = FieldTypeDetailSerializer(self.field_type)
        data = serializer.data
        self.assertEqual(data['id'], self.field_type.id)
        self.assertEqual(data['name'], 'text')
        self.assertEqual(len(data['rules']), 2)
        rules = {rule['rule'] for rule in data['rules']}
        self.assertIn('email', rules)
        self.assertIn('mobile', rules)

class ModuleTypeSerializerTests(TestCase):
    def setUp(self):
        self.module_type = ModuleType.objects.get(name='list')

    def test_module_type_serialization(self):
        serializer = ModuleTypeSerializer(self.module_type)
        data = serializer.data
        self.assertEqual(data['id'], self.module_type.id)
        self.assertEqual(data['name'], 'list')

class UserModuleSerializerTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='password123'
        )
        self.module_type = ModuleType.objects.get(name='list')
        self.user_module = UserModule.objects.create(
            user=self.user,
            module=self.module_type,
            name='My Test List',
            order=1,
            is_enabled=True
        )

    def test_user_module_serialization(self):
        serializer = UserModuleSerializer(self.user_module)
        data = serializer.data
        self.assertEqual(data['id'], self.user_module.id)
        self.assertEqual(data['module'], self.module_type.id)
        self.assertEqual(data['module_name'], 'list')
        self.assertEqual(data['name'], 'My Test List')
        self.assertEqual(data['order'], 1)
        self.assertTrue(data['is_enabled'])
        self.assertFalse(data['is_read_only'])
        self.assertFalse(data['is_checkable'])
        self.assertIn('created_at', data)
        self.assertIn('modified_at', data)

    def test_user_module_creation(self):
        data = {
            'module': self.module_type.id,
            'name': 'New List',
            'order': 2,
            'is_enabled': True,
            'is_read_only': False,
            'is_checkable': True
        }
        serializer = UserModuleSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        user_module = serializer.save(user=self.user)
        self.assertEqual(user_module.name, 'New List')
        self.assertEqual(user_module.order, 2)
        self.assertTrue(user_module.is_enabled)
        self.assertFalse(user_module.is_read_only)
        self.assertTrue(user_module.is_checkable)

class ListFieldSerializerTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='password123'
        )
        self.module_type = ModuleType.objects.get(name='list')
        self.user_module = UserModule.objects.create(
            user=self.user,
            module=self.module_type,
            name='My Test List',
            order=1,
            is_enabled=True
        )
        self.text_field_type = FieldType.objects.get(name='text')
        self.dropdown_field_type = FieldType.objects.get(name='dropdown')
        self.text_rule = FieldTypeRule.objects.get(field_type=self.text_field_type, rule='email')
        self.list_field = ListField.objects.create(
            user_module=self.user_module,
            field_type=self.text_field_type,
            field_name='Task Name',
            is_mandatory=True,
            order=0
        )
        self.field_rule = ListFieldRule.objects.create(
            list_field=self.list_field,
            field_type_rule=self.text_rule
        )

    def test_list_field_serialization(self):
        serializer = ListFieldSerializer(self.list_field)
        data = serializer.data
        self.assertEqual(data['id'], self.list_field.id)
        self.assertEqual(data['field_name'], 'Task Name')
        self.assertEqual(data['field_type'], self.text_field_type.id)
        self.assertTrue(data['is_mandatory'])
        self.assertEqual(data['order'], 0)
        self.assertEqual(len(data['rules']), 1)
        self.assertEqual(data['rules'][0]['field_type_rule']['rule'], 'email')
        self.assertEqual(len(data['options']), 0)  # No options for text field

    def test_dropdown_field_serialization(self):
        # Create a dropdown field with options
        dropdown_type = FieldType.objects.get(name='dropdown')
        dropdown_field = ListField.objects.create(
            user_module=self.user_module,
            field_type=dropdown_type,
            field_name='Priority',
            is_mandatory=False,
            order=1
        )
        option1 = ListFieldOption.objects.create(list_field=dropdown_field, option_name='High')
        option2 = ListFieldOption.objects.create(list_field=dropdown_field, option_name='Medium')
        option3 = ListFieldOption.objects.create(list_field=dropdown_field, option_name='Low')

        serializer = ListFieldSerializer(dropdown_field)
        data = serializer.data
        self.assertEqual(data['field_type'], self.dropdown_field_type.id)
        self.assertEqual(len(data['options']), 3)
        option_names = {option['option_name'] for option in data['options']}
        self.assertIn('High', option_names)
        self.assertIn('Medium', option_names)
        self.assertIn('Low', option_names)

class ListConfigurationSerializerTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='password123'
        )
        self.module_type = ModuleType.objects.get(name='list')
        self.user_module = UserModule.objects.create(
            user=self.user,
            module=self.module_type,
            name='My Test List',
            order=1,
            is_enabled=True
        )
        self.field_type = FieldType.objects.get(name='text')
        self.list_field = ListField.objects.create(
            user_module=self.user_module,
            field_type=self.field_type,
            field_name='Task Name',
            is_mandatory=True,
            order=0
        )

    def test_list_configuration_serialization(self):
        serializer = ListConfigurationSerializer(self.user_module)
        data = serializer.data
        self.assertEqual(data['id'], self.user_module.id)
        self.assertEqual(data['name'], 'My Test List')
        self.assertEqual(data['module_name'], 'list')
        self.assertEqual(len(data['list_fields']), 1)
        self.assertEqual(data['list_fields'][0]['field_name'], 'Task Name')

class ListDataSerializerTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='password123'
        )
        self.module_type = ModuleType.objects.get(name='list')
        self.user_module = UserModule.objects.create(
            user=self.user,
            module=self.module_type,
            name='My Test List',
            order=1,
            is_enabled=True
        )
        self.field_type = FieldType.objects.get(name='text')
        self.list_field = ListField.objects.create(
            user_module=self.user_module,
            field_type=self.field_type,
            field_name='Task Name',
            is_mandatory=True,
            order=0
        )
        self.list_item = ListItem.objects.create(
            user_module=self.user_module,
            is_completed=False,
            fields=[{'field': self.list_field.id, 'value': 'Complete this task'}]
        )

    def test_list_data_serialization(self):
        serializer = ListDataSerializer(self.user_module)
        data = serializer.data
        self.assertEqual(data['id'], self.user_module.id)
        self.assertEqual(data['name'], 'My Test List')
        self.assertEqual(len(data['list_fields']), 1)
        self.assertEqual(data['list_fields'][0]['field_name'], 'Task Name')
        self.assertEqual(len(data['list_items']), 1)
        self.assertEqual(data['list_items'][0]['id'], self.list_item.id)
        self.assertFalse(data['list_items'][0]['is_completed'])
        self.assertEqual(len(data['list_items'][0]['field_values']), 1)
        self.assertEqual(data['list_items'][0]['field_values'][0]['field'], self.list_field.id)
        self.assertEqual(data['list_items'][0]['field_values'][0]['value'], 'Complete this task')

class ListItemSerializerTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='password123'
        )
        self.module_type = ModuleType.objects.get(name='list')
        self.user_module = UserModule.objects.create(
            user=self.user,
            module=self.module_type,
            name='My Test List',
            order=1,
            is_enabled=True
        )
        self.field_type = FieldType.objects.get(name='text')
        self.list_field = ListField.objects.create(
            user_module=self.user_module,
            field_type=self.field_type,
            field_name='Task Name',
            is_mandatory=True,
            order=0
        )
        self.list_item = ListItem.objects.create(
            user_module=self.user_module,
            is_completed=False,
            fields=[{'field': self.list_field.id, 'value': 'Complete this task'}]
        )

    def test_list_item_serialization(self):
        serializer = ListItemSerializer(self.list_item)
        data = serializer.data
        self.assertEqual(data['id'], self.list_item.id)
        self.assertFalse(data['is_completed'])
        self.assertIn('modified_at', data)
        self.assertEqual(len(data['field_values']), 1)
        self.assertEqual(data['field_values'][0]['field'], self.list_field.id)
        self.assertEqual(data['field_values'][0]['value'], 'Complete this task')

    def test_list_item_creation(self):
        data = {
            'is_completed': False,
            'field_values': [
                {'field': self.list_field.id, 'value': 'New task'}
            ]
        }
        serializer = ListItemSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        list_item = serializer.save(user_module=self.user_module)
        self.assertEqual(list_item.user_module, self.user_module)
        self.assertEqual(list_item.fields[0]['value'], 'New task')

    def test_field_values_validation(self):
        # Test with invalid field_values structure
        data = {
            'is_completed': False,
            'field_values': 'not a list'  # Should be a list
        }
        serializer = ListItemSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('field_values', serializer.errors)

        # Test with missing field property
        data = {
            'is_completed': False,
            'field_values': [
                {'value': 'Missing field property'}
            ]
        }
        serializer = ListItemSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('field_values', serializer.errors)

        # Test with missing value property
        data = {
            'is_completed': False,
            'field_values': [
                {'field': self.list_field.id}  # Missing value
            ]
        }
        serializer = ListItemSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('field_values', serializer.errors)

class BudgetCategorySerializerTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='test@example.com', password='testpass123')
        self.module_type = ModuleType.objects.get(name='budget')
        self.user_module = UserModule.objects.create(user=self.user, module=self.module_type, name='My Budget', order=0, is_enabled=True)

    def test_valid_serialization(self):
        category = BudgetCategory.objects.create(user_module=self.user_module, name='Groceries', weekly_target=100, order=0)
        serializer = BudgetCategorySerializer(category)
        self.assertEqual(serializer.data['name'], 'Groceries')
        self.assertEqual(serializer.data['weekly_target'], 100)
        self.assertIn('created_at', serializer.data)

    def test_valid_creation(self):
        data = {
            'name': 'Entertainment',
            'weekly_target': 50,
            'excluded_from_budget': False,
            'order': 1,
            'is_enabled': True
        }
        serializer = BudgetCategorySerializer(data=data, context={'user_module': self.user_module})
        self.assertTrue(serializer.is_valid(), serializer.errors)
        instance = serializer.save(user_module=self.user_module)
        self.assertEqual(instance.name, 'Entertainment')

    def test_duplicate_name_validation(self):
        BudgetCategory.objects.create(user_module=self.user_module, name='Groceries', weekly_target=100, order=0)
        data = {'name': 'Groceries', 'weekly_target': 100, 'excluded_from_budget': False, 'order': 1}
        serializer = BudgetCategorySerializer(data=data, context={'user_module': self.user_module})
        self.assertFalse(serializer.is_valid())
        self.assertIn('name', serializer.errors)

class BudgetPurchaseSerializerTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='test@example.com', password='testpass123')
        self.module_type = ModuleType.objects.get(name='budget')
        self.user_module = UserModule.objects.create(user=self.user, module=self.module_type, name='My Budget', order=0, is_enabled=True)
        self.category = BudgetCategory.objects.create(user_module=self.user_module, name='Groceries', weekly_target=100, order=0)

    def test_valid_serialization(self):
        purchase = BudgetPurchase.objects.create(
            user_module=self.user_module,
            purchase_date='2024-01-01',
            amount=99.99,
            description='Woolworths',
            category=self.category
        )
        serializer = BudgetPurchaseSerializer(purchase)
        self.assertEqual(serializer.data['amount'], '99.99')
        self.assertEqual(serializer.data['category_name'], 'Groceries')

    def test_valid_creation(self):
        data = {
            'purchase_date': '2024-01-02',
            'amount': 20.50,
            'description': 'Snacks',
            'category': self.category.id
        }
        serializer = BudgetPurchaseSerializer(data=data, context={'user_module': self.user_module})
        self.assertTrue(serializer.is_valid(), serializer.errors)
        instance = serializer.save(user_module=self.user_module)
        self.assertEqual(instance.description, 'Snacks')
        self.assertEqual(instance.category, self.category)

    def test_invalid_category(self):
        other_user_module = UserModule.objects.create(user=self.user, module=self.module_type, name='Other Budget', order=1, is_enabled=True)
        other_category = BudgetCategory.objects.create(user_module=other_user_module, name='Other', weekly_target=20, order=0)
        data = {
            'purchase_date': '2024-01-02',
            'amount': 5.00,
            'description': 'Invalid category test',
            'category': other_category.id
        }
        serializer = BudgetPurchaseSerializer(data=data, context={'user_module': self.user_module})
        self.assertFalse(serializer.is_valid())
        self.assertIn('category', serializer.errors)

    def test_bulk_creation(self):
        data = [
            {
                'purchase_date': '2024-01-03',
                'amount': 15.00,
                'description': 'Lunch',
                'category': self.category.id
            },
            {
                'purchase_date': '2024-01-04',
                'amount': 40.00,
                'description': 'Groceries',
                'category': self.category.id
            }
        ]
        serializer = BudgetPurchaseSerializer(data=data, context={'user_module': self.user_module}, many=True)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        instances = serializer.save()
        self.assertEqual(len(instances), 2)
        self.assertEqual(instances[0].description, 'Lunch')
        self.assertEqual(instances[1].amount, 40.00)

class BudgetSerializerTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='test@example.com', password='testpass123')
        self.module_type = ModuleType.objects.get(name='budget')
        self.user_module = UserModule.objects.create(user=self.user, module=self.module_type, name='My Budget', order=0, is_enabled=True)
        BudgetCategory.objects.create(user_module=self.user_module, name='Groceries', weekly_target=50, order=0)
        BudgetCategory.objects.create(user_module=self.user_module, name='Fun', weekly_target=20, order=1)

    def test_budget_serialization_with_categories(self):
        serializer = BudgetSerializer(self.user_module)
        data = serializer.data
        self.assertEqual(data['id'], self.user_module.id)
        self.assertEqual(data['name'], 'My Budget')
        self.assertEqual(len(data['categories']), 2)
        names = [cat['name'] for cat in data['categories']]
        self.assertIn('Groceries', names)
        self.assertIn('Fun', names)