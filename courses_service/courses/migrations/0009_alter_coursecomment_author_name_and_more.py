# Generated by Django 5.0.6 on 2024-07-04 16:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0008_course_author_name_coursecomment_author_name_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='coursecomment',
            name='author_name',
            field=models.CharField(blank=True, max_length=250),
        ),
        migrations.AlterField(
            model_name='lessoncomment',
            name='author_name',
            field=models.CharField(blank=True, max_length=250),
        ),
    ]