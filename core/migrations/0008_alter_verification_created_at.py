# Generated by Django 3.2.6 on 2021-08-14 03:43

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_alter_verification_created_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='verification',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime.now),
        ),
    ]
