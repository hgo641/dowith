# Generated by Django 3.2.6 on 2021-08-13 19:38

import core.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_auto_20210813_1621'),
    ]

    operations = [
        migrations.AlterField(
            model_name='verification',
            name='image_url',
            field=models.ImageField(blank=True, null=True, upload_to=core.models.set_verification_image_name),
        ),
    ]
