# Generated by Django 5.1 on 2024-09-30 15:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0006_profile_specialty4_profile_specialty5'),
    ]

    operations = [
        migrations.RenameField(
            model_name='profile',
            old_name='extra_info1_str',
            new_name='license_number',
        ),
        migrations.RemoveField(
            model_name='profile',
            name='company',
        ),
    ]
