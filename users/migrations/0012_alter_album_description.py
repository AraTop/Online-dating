# Generated by Django 5.0.6 on 2024-11-07 11:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0011_alter_photo_description'),
    ]

    operations = [
        migrations.AlterField(
            model_name='album',
            name='description',
            field=models.TextField(blank=True, max_length=520, null=True),
        ),
    ]
