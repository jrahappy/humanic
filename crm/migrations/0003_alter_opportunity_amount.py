# Generated by Django 5.1 on 2024-11-27 14:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0002_alter_opportunity_agent_alter_opportunity_company_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='opportunity',
            name='amount',
            field=models.DecimalField(decimal_places=2, default=0, help_text='Monthly Amount', max_digits=15),
        ),
    ]