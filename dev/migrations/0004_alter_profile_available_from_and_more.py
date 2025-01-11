# Generated by Django 5.1.4 on 2025-01-11 08:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dev', '0003_alter_skill_options_remove_skill_category'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='available_from',
            field=models.TimeField(blank=True, help_text='Your availability start time (in your timezone)', null=True),
        ),
        migrations.AlterField(
            model_name='profile',
            name='available_to',
            field=models.TimeField(blank=True, help_text='Your availability end time (in your timezone)', null=True),
        ),
    ]
