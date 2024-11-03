# Generated by Django 5.0.6 on 2024-11-03 06:39

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0015_userprofile_orientation_alter_userprofile_gender'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RenameField(
            model_name='userprofile',
            old_name='gender',
            new_name='sex',
        ),
        migrations.AlterUniqueTogether(
            name='userprofile',
            unique_together={('user', 'sex')},
        ),
    ]
