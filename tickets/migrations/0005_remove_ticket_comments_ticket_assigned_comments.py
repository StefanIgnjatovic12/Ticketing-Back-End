# Generated by Django 4.0.1 on 2022-03-05 16:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tickets', '0004_remove_ticket_comments_ticket_comments'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ticket',
            name='comments',
        ),
        migrations.AddField(
            model_name='ticket',
            name='assigned_comments',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='assigned_comments', to='tickets.comment'),
        ),
    ]
