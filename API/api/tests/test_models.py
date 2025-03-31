from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError
from django.core.exceptions import ValidationError
from api.models import (
    ModuleType, UserModule, FieldType, FieldTypeRule,
    ListField, ListFieldRule, ListFieldOption, ListItem
)

User = get_user_model()

class UserModelTests(TestCase):
    def setUp(self):
        self.user_data = {
            'email': 'test@example.com',
            'password': 'securepassword123'
        }
        self.user = User.objects.create_user(**self.user_data)

    def test_user_creation(self):
        self.assertEqual(self.user.email, self.user_data['email'])
        self.assertTrue(self.user.check_password(self.user_data['password']))
        self.assertTrue(self.user.is_active)
        self.assertFalse(self.user.is_staff)

    def test_user_string_representation(self):
        self.assertEqual(str(self.user), self.user_data['email'])

    def test_create_superuser(self):
        admin_user = User.objects.create_superuser(
            email='admin@example.com',
            password='adminpassword123'
        )
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)

    def test_email_required(self):
        with self.assertRaises(ValueError):
            User.objects.create_user(email='', password='password123')

    def test_email_unique(self):
        with self.assertRaises(IntegrityError):
            User.objects.create_user(
                email='test@example.com',  # Same as in setUp
                password='anotherpassword'
            )

class ModuleTypeTests(TestCase):
    def setUp(self):
        self.module_type = ModuleType.objects.create(name='list')

    def test_module_type_creation(self):
        self.assertEqual(self.module_type.name, 'list')

    def test_module_type_string_representation(self):
        self.assertEqual(str(self.module_type), 'list')

class UserModuleTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='password123'
        )
        self.module_type = ModuleType.objects.create(name='list')
        self.user_module = UserModule.objects.create(
            user=self.user,
            module=self.module_type,
            name='My Test List',
            order=1,
            is_enabled=True
        )

    def test_user_module_creation(self):
        self.assertEqual(self.user_module.user, self.user)
        self.assertEqual(self.user_module.module, self.module_type)
        self.assertEqual(self.user_module.name, 'My Test List')
        self.assertEqual(self.user_module.order, 1)
        self.assertTrue(self.user_module.is_enabled)
        self.assertFalse(self.user_module.is_read_only)
        self.assertFalse(self.user_module.is_checkable)

    def test_user_module_string_representation(self):
        self.assertEqual(str(self.user_module), 'My Test List')

    def test_created_at_and_modified_at_auto_fields(self):
        self.assertIsNotNone(self.user_module.created_at)
        self.assertIsNotNone(self.user_module.modified_at)

class FieldTypeTests(TestCase):
    def setUp(self):
        self.field_type = FieldType.objects.create(name='text')

    def test_field_type_creation(self):
        self.assertEqual(self.field_type.name, 'text')

    def test_field_type_string_representation(self):
        self.assertEqual(str(self.field_type), 'text')

class FieldTypeRuleTests(TestCase):
    def setUp(self):
        self.field_type = FieldType.objects.create(name='number')
        self.field_rule = FieldTypeRule.objects.create(
            field_type=self.field_type,
            rule='min_value'
        )

    def test_field_type_rule_creation(self):
        self.assertEqual(self.field_rule.field_type, self.field_type)
        self.assertEqual(self.field_rule.rule, 'min_value')

    def test_field_type_rule_string_representation(self):
        self.assertEqual(str(self.field_rule), 'min_value')

class ListFieldTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='password123'
        )
        self.module_type = ModuleType.objects.create(name='list')
        self.user_module = UserModule.objects.create(
            user=self.user,
            module=self.module_type,
            name='My Test List',
            order=1,
            is_enabled=True
        )
        self.field_type = FieldType.objects.create(name='text')
        self.list_field = ListField.objects.create(
            user_module=self.user_module,
            field_type=self.field_type,
            field_name='Task Name',
            is_mandatory=True,
            order=0
        )

    def test_list_field_creation(self):
        self.assertEqual(self.list_field.user_module, self.user_module)
        self.assertEqual(self.list_field.field_type, self.field_type)
        self.assertEqual(self.list_field.field_name, 'Task Name')
        self.assertTrue(self.list_field.is_mandatory)
        self.assertEqual(self.list_field.order, 0)

    def test_list_field_string_representation(self):
        self.assertEqual(str(self.list_field), 'Task Name')

class ListFieldRuleTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='password123'
        )
        self.module_type = ModuleType.objects.create(name='list')
        self.user_module = UserModule.objects.create(
            user=self.user,
            module=self.module_type,
            name='My Test List',
            order=1,
            is_enabled=True
        )
        self.field_type = FieldType.objects.create(name='text')
        self.field_type_rule = FieldTypeRule.objects.create(
            field_type=self.field_type,
            rule='max_length'
        )
        self.list_field = ListField.objects.create(
            user_module=self.user_module,
            field_type=self.field_type,
            field_name='Task Name',
            is_mandatory=True,
            order=0
        )
        self.list_field_rule = ListFieldRule.objects.create(
            list_field=self.list_field,
            field_type_rule=self.field_type_rule
        )

    def test_list_field_rule_creation(self):
        self.assertEqual(self.list_field_rule.list_field, self.list_field)
        self.assertEqual(self.list_field_rule.field_type_rule, self.field_type_rule)

    def test_list_field_rule_string_representation(self):
        self.assertEqual(str(self.list_field_rule), 'Task Name - max_length')

class ListFieldOptionTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='password123'
        )
        self.module_type = ModuleType.objects.create(name='list')
        self.user_module = UserModule.objects.create(
            user=self.user,
            module=self.module_type,
            name='My Test List',
            order=1,
            is_enabled=True
        )
        self.field_type = FieldType.objects.create(name='dropdown')
        self.list_field = ListField.objects.create(
            user_module=self.user_module,
            field_type=self.field_type,
            field_name='Priority',
            is_mandatory=True,
            order=0
        )
        self.option = ListFieldOption.objects.create(
            list_field=self.list_field,
            option_name='High'
        )

    def test_list_field_option_creation(self):
        self.assertEqual(self.option.list_field, self.list_field)
        self.assertEqual(self.option.option_name, 'High')

    def test_list_field_option_string_representation(self):
        self.assertEqual(str(self.option), 'High')

class ListItemTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='password123'
        )
        self.module_type = ModuleType.objects.create(name='list')
        self.user_module = UserModule.objects.create(
            user=self.user,
            module=self.module_type,
            name='My Test List',
            order=1,
            is_enabled=True
        )
        self.field_type = FieldType.objects.create(name='text')
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

    def test_list_item_creation(self):
        self.assertEqual(self.list_item.user_module, self.user_module)
        self.assertFalse(self.list_item.is_completed)
        self.assertEqual(len(self.list_item.fields), 1)
        self.assertEqual(self.list_item.fields[0]['field'], self.list_field.id)
        self.assertEqual(self.list_item.fields[0]['value'], 'Complete this task')

    def test_list_item_string_representation(self):
        # Check that the string representation contains the expected parts
        self.assertIn(self.user_module.name, str(self.list_item))
        # Should also have a date in the string representation
        self.assertIn(str(self.list_item.modified_at.year), str(self.list_item))

    def test_modified_at_auto_update(self):
        original_modified_at = self.list_item.modified_at

        # Update the list item
        self.list_item.is_completed = True
        self.list_item.save()

        # Refresh from DB
        self.list_item.refresh_from_db()

        # Check that modified_at has been updated
        self.assertNotEqual(self.list_item.modified_at, original_modified_at)

    def test_json_field_structure(self):
        # Test that we can store complex JSON
        complex_fields = [
            {'field': self.list_field.id, 'value': 'Task 1'},
            {'field': 999, 'value': 'This field doesn\'t exist but JSON can store it'}
        ]

        self.list_item.fields = complex_fields
        self.list_item.save()

        # Refresh from DB
        self.list_item.refresh_from_db()

        # Check that the JSON structure is preserved
        self.assertEqual(len(self.list_item.fields), 2)
        self.assertEqual(self.list_item.fields[0]['value'], 'Task 1')
        self.assertEqual(self.list_item.fields[1]['field'], 999)