# Generated by Django 5.1 on 2024-09-14 03:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('minibooks', '0005_reportmaster_platform'),
    ]

    operations = [
        migrations.AddField(
            model_name='reportmaster',
            name='unverified_message',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='reportmaster',
            name='approvedt',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='reportmaster',
            name='requestdt',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]