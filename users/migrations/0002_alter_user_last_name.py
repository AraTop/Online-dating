# Generated by Django 5.0.6 on 2024-06-15 20:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='last_name',
            field=models.CharField(default=1, max_length=40, verbose_name='Фамилия'),
            preserve_default=False,
        ),
    ]
