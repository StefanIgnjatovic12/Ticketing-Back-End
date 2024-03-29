# Generated by Django 4.0.1 on 2022-03-30 17:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tickets', '0034_remove_historicalticket_assigned_developer_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historicalticket',
            name='status',
            field=models.CharField(blank=True, choices=[('Unassigned', 'Unassigned'), ('Assigned/In progress', 'Assigned/In progress'), ('Resolved', 'Resolved')], default='Unassigned', max_length=50),
        ),
        migrations.AlterField(
            model_name='ticket',
            name='status',
            field=models.CharField(blank=True, choices=[('Unassigned', 'Unassigned'), ('Assigned/In progress', 'Assigned/In progress'), ('Resolved', 'Resolved')], default='Unassigned', max_length=50),
        ),
    ]
