# Generated by Django 5.1 on 2024-11-08 23:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0012_rename_hoiiday_date_holidays_hoiidays'),
    ]

    operations = [
        migrations.AlterField(
            model_name='holidays',
            name='hoiidays',
            field=models.JSONField(default=list),
        ),
    ]