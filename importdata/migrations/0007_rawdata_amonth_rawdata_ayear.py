# Generated by Django 5.1 on 2024-09-05 02:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('importdata', '0006_alter_importhistory_source_from'),
    ]

    operations = [
        migrations.AddField(
            model_name='rawdata',
            name='amonth',
            field=models.CharField(blank=True, max_length=5, null=True),
        ),
        migrations.AddField(
            model_name='rawdata',
            name='ayear',
            field=models.CharField(blank=True, max_length=5, null=True),
        ),
    ]