# Generated by Django 5.1 on 2024-11-19 15:03

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0015_company_customuser'),
    ]

    operations = [
        migrations.AddField(
            model_name='servicefee',
            name='service_company',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='service_company', to='customer.company'),
        ),
    ]