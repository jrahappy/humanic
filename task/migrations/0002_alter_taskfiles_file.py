# Generated by Django 5.1 on 2024-12-28 22:38

import task.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('task', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='taskfiles',
            name='file',
            field=models.FileField(blank=True, max_length=250, null=True, upload_to=task.models.TaskFiles.upload_location),
        ),
    ]