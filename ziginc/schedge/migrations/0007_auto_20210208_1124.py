# Generated by Django 3.1.5 on 2021-02-08 11:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('schedge', '0006_auto_20210208_1122'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='image',
            field=models.ImageField(default='default.jpg', upload_to=''),
        ),
    ]
