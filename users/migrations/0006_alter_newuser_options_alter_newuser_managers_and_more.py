# Generated by Django 5.0.7 on 2024-08-02 21:46

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_alter_newuser_options_alter_newuser_managers_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='newuser',
            options={},
        ),
        migrations.AlterModelManagers(
            name='newuser',
            managers=[
            ],
        ),
        migrations.RemoveField(
            model_name='newuser',
            name='date_joined',
        ),
        migrations.AddField(
            model_name='newuser',
            name='start_date',
            field=models.DateField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='newuser',
            name='first_name',
            field=models.CharField(max_length=150, verbose_name='first_name'),
        ),
        migrations.AlterField(
            model_name='newuser',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='newuser',
            name='is_staff',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='newuser',
            name='last_name',
            field=models.CharField(max_length=150, verbose_name='last_name'),
        ),
        migrations.DeleteModel(
            name='Profile',
        ),
    ]
