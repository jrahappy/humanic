# Generated by Django 5.1 on 2024-09-16 22:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('minibooks', '0009_uploadhistorytrack_is_deleted'),
    ]

    operations = [
        migrations.AddField(
            model_name='reportmaster',
            name='exelrownum',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='reportmaster',
            name='pay_to_provider',
            field=models.FloatField(blank=True, default=0, null=True),
        ),
    ]