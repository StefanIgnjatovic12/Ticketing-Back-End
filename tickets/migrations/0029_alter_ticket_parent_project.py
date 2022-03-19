# Generated by Django 4.0.1 on 2022-03-19 17:15

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0004_remove_project_assigned_tickets'),
        ('tickets', '0028_rename_parent_ticket_historicalticket_parent_project_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ticket',
            name='parent_project',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='tickets', to='projects.project'),
        ),
    ]
