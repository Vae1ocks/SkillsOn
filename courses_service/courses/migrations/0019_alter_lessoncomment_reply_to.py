# Generated by Django 5.0.7 on 2024-09-17 18:58

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0018_lessoncomment_is_note_lessoncomment_quote_text_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lessoncomment',
            name='reply_to',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='replies', to='courses.lessoncomment'),
        ),
    ]
