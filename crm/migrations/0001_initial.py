# Generated by Django 5.1 on 2024-11-25 02:59

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('customer', '0022_alter_company_tags'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Chance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20)),
                ('purpose', models.CharField(max_length=250)),
                ('phone', models.CharField(blank=True, max_length=20, null=True)),
                ('email', models.EmailField(blank=True, max_length=254, null=True)),
                ('sns', models.CharField(blank=True, max_length=100, null=True)),
                ('stage', models.CharField(choices=[('Potential', 'Potential'), ('Qualified', 'Qualified'), ('Working', 'Working'), ('Closed', 'Closed'), ('Pending', 'Pending'), ('Lost', 'Lost')], max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('agent', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Chance',
                'verbose_name_plural': 'Chances',
            },
        ),
        migrations.CreateModel(
            name='ChanceComment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comment', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('chance', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='history', to='crm.chance')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Opportunity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True, null=True)),
                ('amount', models.DecimalField(decimal_places=2, default=0, help_text='Monthly Amount', max_digits=10)),
                ('possibility', models.IntegerField(default=0, help_text='Percentage', validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)])),
                ('target_date', models.DateField(blank=True, null=True)),
                ('category', models.CharField(choices=[('Sale', 'Sale'), ('Support', 'Support'), ('Issue', 'Issue')], max_length=20)),
                ('stage', models.CharField(choices=[('Potential', 'Potential'), ('Qualified', 'Qualified'), ('Working', 'Working'), ('Closed', 'Closed'), ('Pending', 'Pending'), ('Lost', 'Lost')], max_length=20)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('agent', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='opportunities', to=settings.AUTH_USER_MODEL)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='opportunities', to='customer.company')),
            ],
            options={
                'verbose_name': 'Opportunity',
                'verbose_name_plural': 'Opportunites',
            },
        ),
        migrations.CreateModel(
            name='Note',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('note', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('opportunity', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notes', to='crm.opportunity')),
            ],
            options={
                'verbose_name': 'Note',
                'verbose_name_plural': 'Notes',
            },
        ),
        migrations.CreateModel(
            name='OpportunityHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stage', models.CharField(choices=[('Potential', 'Potential'), ('Qualified', 'Qualified'), ('Working', 'Working'), ('Closed', 'Closed'), ('Pending', 'Pending'), ('Lost', 'Lost')], max_length=20)),
                ('possibility', models.IntegerField(default=0, help_text='Percentage', validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)])),
                ('changed_at', models.DateTimeField(auto_now_add=True)),
                ('opportunity', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='history', to='crm.opportunity')),
            ],
            options={
                'verbose_name': 'Opportunity History',
                'verbose_name_plural': 'Opportunity Histories',
            },
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('task', models.TextField()),
                ('due_date', models.DateField()),
                ('completed', models.BooleanField(default=False)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('opportunity', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tasks', to='crm.opportunity')),
            ],
            options={
                'verbose_name': 'Task',
                'verbose_name_plural': 'Tasks',
            },
        ),
    ]