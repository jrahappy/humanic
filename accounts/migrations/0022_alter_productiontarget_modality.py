# Generated by Django 5.1 on 2024-11-16 16:29

import utils.base_func
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0021_alter_productiontarget_work_weekday'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productiontarget',
            name='modality',
            field=models.CharField(choices=utils.base_func.get_amodality_choices, max_length=10),
        ),
    ]
