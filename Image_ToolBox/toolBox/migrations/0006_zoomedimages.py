# Generated by Django 3.2.8 on 2021-12-21 20:07

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('toolBox', '0005_blendingwithcurrentimage'),
    ]

    operations = [
        migrations.CreateModel(
            name='ZoomedImages',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('width', models.PositiveBigIntegerField(default=0)),
                ('height', models.PositiveBigIntegerField(default=0)),
                ('x_position', models.PositiveBigIntegerField(default=0)),
                ('y_position', models.PositiveBigIntegerField(default=0)),
                ('zoomed_image', models.ImageField(default='zoomedImages/p.png', upload_to='zoomedImages/')),
                ('target_image', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='toolBox.projectsimages')),
            ],
        ),
    ]
