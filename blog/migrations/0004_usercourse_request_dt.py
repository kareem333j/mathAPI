# Generated by Django 5.0.7 on 2024-09-30 19:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0003_grade_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='usercourse',
            name='request_dt',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
    ]
