# Generated by Django 5.0.6 on 2024-07-02 15:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_userstatus'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='is_online',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='user',
            name='last_activity',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.DeleteModel(
            name='UserStatus',
        ),
    ]
