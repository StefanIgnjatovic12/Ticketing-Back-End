# Generated by Django 4.0.1 on 2022-03-14 16:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tickets', '0021_attachment_created_on'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attachment',
            name='created_on',
            field=models.CharField(max_length=20, null=True),
        ),
    ]
