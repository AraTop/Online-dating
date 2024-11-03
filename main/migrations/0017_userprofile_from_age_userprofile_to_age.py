# Generated by Django 5.0.6 on 2024-11-03 06:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0016_rename_gender_userprofile_sex_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='from_age',
            field=models.IntegerField(default=10, max_length=10),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='userprofile',
            name='to_age',
            field=models.IntegerField(default=20, max_length=15),
            preserve_default=False,
        ),
    ]