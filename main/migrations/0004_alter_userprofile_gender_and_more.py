# Generated by Django 5.0.6 on 2024-07-24 15:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_alter_userprofile_gender'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='gender',
            field=models.CharField(blank=True, choices=[('male', 'Мужской'), ('female', 'Женский'), ('other', 'Другой')], max_length=15, null=True),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='looking_for',
            field=models.CharField(blank=True, max_length=15, null=True),
        ),
    ]
