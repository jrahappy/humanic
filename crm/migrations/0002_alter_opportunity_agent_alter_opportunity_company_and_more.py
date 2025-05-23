# Generated by Django 5.1 on 2024-11-25 13:54

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0001_initial'),
        ('customer', '0022_alter_company_tags'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='opportunity',
            name='agent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='opportunities', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='opportunity',
            name='company',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='opportunities', to='customer.company'),
        ),
        migrations.AlterField(
            model_name='opportunity',
            name='possibility',
            field=models.IntegerField(default=50, help_text='Percentage', validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)]),
        ),
    ]
