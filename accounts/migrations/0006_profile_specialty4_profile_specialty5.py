# Generated by Django 5.1 on 2024-09-18 14:56

import utils.base_func
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_alter_profile_specialty2_alter_profile_specialty3'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='specialty4',
            field=models.CharField(blank=True, choices=utils.base_func.get_specialty_choices, max_length=30, null=True),
        ),
        migrations.AddField(
            model_name='profile',
            name='specialty5',
            field=models.CharField(blank=True, choices=utils.base_func.get_specialty_choices, max_length=30, null=True),
        ),
    ]