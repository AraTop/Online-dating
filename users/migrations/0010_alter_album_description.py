# Generated by Django 5.0.6 on 2024-11-06 13:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0009_album_photo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='album',
            name='description',
            field=models.TextField(blank=True, max_length=255, null=True),
        ),
    ]