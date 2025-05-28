from django.db import migrations


def add_period_data(apps, schema_editor):
    # Get the models
    Period = apps.get_model('api', 'Period')

    # Create periods
    Period.objects.create(name='daily')
    Period.objects.create(name='weekly')
    Period.objects.create(name='monthly')
    Period.objects.create(name='yearly')


def remove_period_data(apps, schema_editor):
    # Get the models
    Period = apps.get_model('api', 'Period')

    # Delete all data
    Period.objects.all().delete()

class Migration(migrations.Migration):

    dependencies = [
        ('api', '0007_period_budgetcashflow'),
    ]

    operations = [
        migrations.RunPython(add_period_data, remove_period_data),
    ]