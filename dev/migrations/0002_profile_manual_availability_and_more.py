# Generated by Django 5.1.4 on 2025-01-11 19:22

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dev', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='manual_availability',
            field=models.BooleanField(default=False, help_text='Override automatic availability'),
        ),
        migrations.AddField(
            model_name='profile',
            name='manual_availability_end',
            field=models.DateTimeField(blank=True, help_text='When manual availability should end', null=True),
        ),
        migrations.AlterField(
            model_name='project',
            name='deployed_url',
            field=models.URLField(blank=True, max_length=500),
        ),
        migrations.AlterField(
            model_name='project',
            name='github_url',
            field=models.URLField(max_length=500),
        ),
        migrations.AlterField(
            model_name='project',
            name='profile',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='projects', to='dev.profile'),
        ),
    ]
