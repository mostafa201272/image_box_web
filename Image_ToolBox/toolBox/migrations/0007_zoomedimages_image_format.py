# Generated by Django 3.2.8 on 2021-12-21 20:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('toolBox', '0006_zoomedimages'),
    ]

    operations = [
        migrations.AddField(
            model_name='zoomedimages',
            name='image_format',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
