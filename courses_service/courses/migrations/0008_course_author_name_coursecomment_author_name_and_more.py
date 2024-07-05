# Generated by Django 5.0.6 on 2024-07-04 16:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0007_remove_file_created_remove_image_created_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='author_name',
            field=models.CharField(default='Admin A.', max_length=250),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='coursecomment',
            name='author_name',
            field=models.CharField(default='Admin A.', max_length=250),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='lessoncomment',
            name='author_name',
            field=models.CharField(default='Admin A.', max_length=250),
            preserve_default=False,
        ),
    ]
