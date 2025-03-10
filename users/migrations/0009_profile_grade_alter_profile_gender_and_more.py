# Generated by Django 5.0.7 on 2024-08-03 17:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0008_profile_gender_alter_profile_state'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='grade',
            field=models.CharField(blank=True, choices=[('الصف الأول الثانوي', 'الصف الأول الثانوي'), ('الصف الثاني الثانوي', 'الصف الثاني الثانوي'), ('الصف الثالث الثانوي', 'الصف الثالث الثانوي')], max_length=100),
        ),
        migrations.AlterField(
            model_name='profile',
            name='gender',
            field=models.CharField(choices=[('ذكر', 'ذكر'), ('انثي', 'انثي')], max_length=100),
        ),
        migrations.AlterField(
            model_name='profile',
            name='parent_phone',
            field=models.CharField(max_length=11, unique=True, verbose_name='parent number'),
        ),
    ]
