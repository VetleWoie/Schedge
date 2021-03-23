# Generated by Django 3.1.5 on 2021-03-23 16:15

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('schedge', '0002_auto_20210318_1239'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='potentialtimeslot',
            name='event',
        ),
        migrations.AddField(
            model_name='event',
            name='chosen_timeslot',
            field=models.OneToOneField(default=0, on_delete=django.db.models.deletion.CASCADE, related_name='event', to='schedge.potentialtimeslot'),
        ),
        migrations.AlterField(
            model_name='event',
            name='status',
            field=models.CharField(choices=[('C', 'Chosen'), ('U', 'Unresolved'), ('F', 'Finished')], default='U', max_length=10),
        ),
    ]
