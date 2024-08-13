# Generated by Django 5.0.7 on 2024-08-02 12:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0014_alter_lesson_users_seen'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='author_image',
            field=models.ImageField(blank=True, null=True, upload_to='courses/%Y/%m/%d/'),
        ),
        migrations.AddField(
            model_name='coursecomment',
            name='author_image',
            field=models.ImageField(blank=True, null=True, upload_to='comments/%Y/%m/%d/'),
        ),
        migrations.AddField(
            model_name='lessoncomment',
            name='author_image',
            field=models.ImageField(blank=True, null=True, upload_to='comments/%Y/%m/%d/'),
        ),
    ]