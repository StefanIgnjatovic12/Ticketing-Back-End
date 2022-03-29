# Generated by Django 4.0.1 on 2022-03-26 17:52

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('projects', '0005_alter_project_assigned_users'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='assigned_users',
            field=models.ManyToManyField(blank=True, related_name='assigned_users', to=settings.AUTH_USER_MODEL),
        ),
    ]
