# Generated by Django 3.2.6 on 2021-08-12 07:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0002_refreshtoken'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='image_url',
        ),
        migrations.AddField(
            model_name='user',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to=''),
        ),
    ]
