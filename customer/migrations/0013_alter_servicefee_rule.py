# Generated by Django 5.1 on 2024-10-01 17:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0012_contract_service_fee_servicefee_rule'),
    ]

    operations = [
        migrations.AlterField(
            model_name='servicefee',
            name='rule',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
    ]
