# Generated by Django 5.0.7 on 2024-11-28 12:38

import courses.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("courses", "0019_alter_lessoncomment_reply_to"),
    ]

    operations = [
        migrations.AddField(
            model_name="category",
            name="image",
            field=models.ImageField(
                blank=True, null=True, upload_to=courses.models.category_image_upload_to
            ),
        ),
    ]
