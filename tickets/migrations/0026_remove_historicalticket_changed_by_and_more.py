# Generated by Django 4.0.1 on 2022-03-18 17:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tickets', '0025_historicalticket_changed_by_ticket_changed_by'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='historicalticket',
            name='changed_by',
        ),
        migrations.RemoveField(
            model_name='ticket',
            name='changed_by',
        ),
    ]