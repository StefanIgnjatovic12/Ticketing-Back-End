# Generated by Django 4.0.1 on 2022-03-07 17:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tickets', '0008_historicalticket'),
    ]

    operations = [
        migrations.DeleteModel(
            name='HistoricalTicket',
        ),
    ]
