# Generated by Django 5.0.6 on 2024-07-04 16:20

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0002_remove_user_profile_picture'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='date_joined',
            field=models.DateTimeField(default=datetime.datetime(2024, 7, 4, 16, 20, 24, 437008, tzinfo=datetime.timezone.utc)),
        ),
    ]
