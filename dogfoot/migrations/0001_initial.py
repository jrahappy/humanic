# Generated by Django 5.1 on 2024-09-09 03:14

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='MegaChoiceNames',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20)),
                ('order', models.IntegerField(default=0)),
                ('memo', models.CharField(blank=True, max_length=100, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='MegaMenu',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20)),
                ('description', models.CharField(blank=True, max_length=200, null=True)),
                ('int_field', models.IntegerField(default=0)),
                ('char_field', models.CharField(blank=True, max_length=20, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='MegaChoices',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('c0', models.CharField(max_length=20)),
                ('c1', models.CharField(max_length=20)),
                ('c2', models.CharField(blank=True, max_length=20, null=True)),
                ('order', models.IntegerField(default=0)),
                ('name', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dogfoot.megachoicenames')),
            ],
        ),
        migrations.CreateModel(
            name='MegaMenuSub',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sub_name', models.CharField(max_length=20)),
                ('url', models.CharField(blank=True, max_length=100, null=True)),
                ('int_field', models.IntegerField(default=0)),
                ('char_field', models.CharField(blank=True, max_length=20, null=True)),
                ('orderx', models.IntegerField(default=0)),
                ('ordery', models.IntegerField(default=0)),
                ('is_active', models.BooleanField(default=True)),
                ('css_class', models.CharField(blank=True, max_length=40, null=True)),
                ('ajax_attr0', models.CharField(blank=True, max_length=20, null=True)),
                ('ajax_attr1', models.CharField(blank=True, max_length=20, null=True)),
                ('ajax_attr2', models.CharField(blank=True, max_length=20, null=True)),
                ('ajax_attr4', models.CharField(blank=True, max_length=20, null=True)),
                ('name', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dogfoot.megamenu')),
            ],
        ),
    ]