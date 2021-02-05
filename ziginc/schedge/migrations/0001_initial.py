# Generated by Django 3.1.5 on 2021-02-05 13:20

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('startDate', models.DateField()),
                ('enddate', models.DateField()),
                ('startTime', models.TimeField()),
                ('endTime', models.TimeField()),
                ('duration', models.DurationField()),
                ('description', models.CharField(max_length=500)),
                ('location', models.CharField(max_length=100)),
            ],
        ),
    ]
