# Generated by Django 5.1 on 2024-11-22 15:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('minibooks', '0035_reportmaster_adate'),
    ]

    operations = [
        migrations.AddField(
            model_name='magamaccounting',
            name='adate',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='magammaster',
            name='adate',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='reportmasterperformance',
            name='adate',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='reportmasterstat',
            name='adate',
            field=models.DateField(blank=True, null=True),
        ),
    ]