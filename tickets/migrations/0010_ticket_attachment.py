# Generated by Django 4.0.1 on 2022-03-08 18:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tickets', '0009_delete_historicalticket'),
    ]

    operations = [
        migrations.AddField(
            model_name='ticket',
            name='attachment',
            field=models.FileField(null=True, upload_to=''),
        ),
    ]
