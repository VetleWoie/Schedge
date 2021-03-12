# Generated by Django 3.1.5 on 2021-03-11 09:22

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('location', models.CharField(max_length=300)),
                ('description', models.TextField(blank=True, max_length=500)),
                ('starttime', models.TimeField(default=django.utils.timezone.now)),
                ('endtime', models.TimeField(default=django.utils.timezone.now)),
                ('startdate', models.DateField(default=django.utils.timezone.now)),
                ('enddate', models.DateField(default=django.utils.timezone.now)),
                ('duration', models.DurationField(default=datetime.timedelta(0), max_length=datetime.timedelta(seconds=36000))),
                ('image', models.ImageField(default='default.jpg', upload_to='images/')),
                ('status', models.CharField(choices=[('C', 'Concluded'), ('U', 'Unresolved')], default='U', max_length=10)),
                ('host', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Participant',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ishost', models.BooleanField(default=False)),
                ('event', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='schedge.event')),
                ('user', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='TimeSlot',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_time', models.TimeField()),
                ('end_time', models.TimeField()),
                ('date', models.DateField()),
                ('creator', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='schedge.event')),
            ],
            options={
                'unique_together': {('event', 'start_time', 'end_time', 'date')},
            },
        ),
    ]
