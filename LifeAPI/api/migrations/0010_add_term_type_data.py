from django.db import migrations

def add_term_type_data(apps, schema_editor):
    TermType = apps.get_model('api', 'BudgetTermType')

    TermType.objects.create(word_length=1, weight=1)
    TermType.objects.create(word_length=2, weight=3)
    TermType.objects.create(word_length=3, weight=5)

def remove_term_type_data(apps, schema_editor):
    TermType = apps.get_model('api', 'BudgetTermType')

    TermType.objects.all().delete()

class Migration(migrations.Migration):

    dependencies = [
        ('api', '0009_budgettermtype_budgetcategorytermfrequency'),
    ]

    operations = [
        migrations.RunPython(add_term_type_data, remove_term_type_data),
    ]
