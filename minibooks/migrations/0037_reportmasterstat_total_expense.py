# Generated by Django 5.1 on 2024-11-22 17:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('minibooks', '0036_magamaccounting_adate_magammaster_adate_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='reportmasterstat',
            name='total_expense',
            field=models.FloatField(blank=True, default=0, null=True),
        ),
    ]