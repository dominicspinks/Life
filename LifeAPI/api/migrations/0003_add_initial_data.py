from django.db import migrations

def add_initial_data(apps, schema_editor):
    # Get the models
    ModuleType = apps.get_model('api', 'ModuleType')
    FieldType = apps.get_model('api', 'FieldType')
    FieldTypeRule = apps.get_model('api', 'FieldTypeRule')

    # Create module types
    budget = ModuleType.objects.create(name='budget')
    list_type = ModuleType.objects.create(name='list')

    # Create field types
    dropdown = FieldType.objects.create(name='dropdown')
    text = FieldType.objects.create(name='text')
    date = FieldType.objects.create(name='date')
    number = FieldType.objects.create(name='number')

    # Create field type rules
    # For text type
    FieldTypeRule.objects.create(field_type=text, rule='email')
    FieldTypeRule.objects.create(field_type=text, rule='mobile')

    # For number type
    FieldTypeRule.objects.create(field_type=number, rule='positive_only')
    FieldTypeRule.objects.create(field_type=number, rule='integer')
    FieldTypeRule.objects.create(field_type=number, rule='money')

def remove_initial_data(apps, schema_editor):
    # Get the models
    ModuleType = apps.get_model('api', 'ModuleType')
    FieldType = apps.get_model('api', 'FieldType')
    FieldTypeRule = apps.get_model('api', 'FieldTypeRule')

    # Delete all data
    FieldTypeRule.objects.all().delete()
    FieldType.objects.all().delete()
    ModuleType.objects.all().delete()

class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_fieldtype_listitem_moduletype_fieldtyperule_and_more'),
    ]

    operations = [
        migrations.RunPython(add_initial_data, remove_initial_data),
    ]
