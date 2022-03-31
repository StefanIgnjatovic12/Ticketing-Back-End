# Generated by Django 4.0.1 on 2022-03-30 17:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tickets', '0033_historicalticket_assigned_developer_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='historicalticket',
            name='assigned_developer',
        ),
        migrations.AddField(
            model_name='historicalticket',
            name='status',
            field=models.CharField(choices=[('Unassigned', 'Unassigned'), ('Assigned/In progress', 'Assigned/In progress'), ('Resolved', 'Resolved')], default='Unassigned', max_length=50),
        ),
        migrations.AddField(
            model_name='historicalticket',
            name='type',
            field=models.CharField(choices=[('Bug report', 'Bug report'), ('Feature request', 'Feature request'), ('Not specified', 'Not specified'), ('Other', 'Other')], default='Not specified', max_length=50),
        ),
        migrations.AddField(
            model_name='ticket',
            name='status',
            field=models.CharField(choices=[('Unassigned', 'Unassigned'), ('Assigned/In progress', 'Assigned/In progress'), ('Resolved', 'Resolved')], default='Unassigned', max_length=50),
        ),
        migrations.AddField(
            model_name='ticket',
            name='type',
            field=models.CharField(choices=[('Bug report', 'Bug report'), ('Feature request', 'Feature request'), ('Not specified', 'Not specified'), ('Other', 'Other')], default='Not specified', max_length=50),
        ),
    ]
