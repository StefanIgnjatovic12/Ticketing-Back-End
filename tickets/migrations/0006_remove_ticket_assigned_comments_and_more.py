# Generated by Django 4.0.1 on 2022-03-05 16:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tickets', '0005_remove_ticket_comments_ticket_assigned_comments'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ticket',
            name='assigned_comments',
        ),
        migrations.AddField(
            model_name='comment',
            name='parent_ticket',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='tickets.ticket'),
        ),
    ]
