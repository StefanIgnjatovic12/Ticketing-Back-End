# Generated by Django 4.0.1 on 2022-03-19 16:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0004_remove_project_assigned_tickets'),
        ('tickets', '0026_remove_historicalticket_changed_by_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalticket',
            name='parent_ticket',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='projects.project'),
        ),
        migrations.AddField(
            model_name='ticket',
            name='parent_ticket',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='parent_ticket', to='projects.project'),
        ),
    ]
