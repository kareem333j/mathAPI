# Generated by Django 5.0.7 on 2024-11-07 11:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0013_notification_created_dt'),
    ]

    operations = [
        migrations.AddField(
            model_name='usernotificationinfo',
            name='created_dt',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
    ]
