# Generated by Django 5.1 on 2025-01-07 02:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('collab', '0020_alter_refers_url'),
    ]

    operations = [
        migrations.AddField(
            model_name='refers',
            name='refer_doctor',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]