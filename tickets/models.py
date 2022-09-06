import pathlib

from django.db import models


from django.contrib.auth.models import User
from django.utils import timezone
from django.conf import settings
from django.urls import reverse
from simple_history.models import HistoricalRecords
from projects.models import Project
from api.validators import validate_file_type

class Ticket(models.Model):
    PRIORITY_CHOICES = [
        ('Urgent', 'Urgent'),
        ('High', 'High'),
        ('Medium', 'Medium'),
        ('Low', 'Low')
    ]

    TICKET_TYPE_CHOICES = [
        ('Bug report', 'Bug report'),
        ('Feature request', 'Feature request'),
        ('Not specified', 'Not specified'),
        ('Other', 'Other')
    ]

    TICKET_STATUS = [
        ('Unassigned', 'Unassigned'),
        ('Assigned/In progress', 'Assigned/In progress'),
        ('Resolved', 'Resolved'),
    ]
    title = models.CharField(max_length=100, blank=True)
    description = models.TextField(default='', blank=True)
    created_on = models.CharField(max_length=20, null=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    priority = models.CharField(max_length=6, choices=PRIORITY_CHOICES, default='low')
    type = models.CharField(max_length=50, choices=TICKET_TYPE_CHOICES, default='Not specified')
    status = models.CharField(max_length=50, choices=TICKET_STATUS, default='Unassigned', blank=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tickets', null=True)
    update_time =  models.CharField(max_length=100, blank=True)
    history = HistoricalRecords(excluded_fields=['update_time', 'assigned_developer'])
    assigned_developer = models.ForeignKey(User,
                                           on_delete=models.CASCADE,
                                           related_name="assigned_developer",
                                           null=True)

    def __str__(self):
        return self.title




class Comment(models.Model):
    content = models.TextField(default='', blank=False)
    parent_ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, null=True, related_name="comments")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_on = models.CharField(max_length=20, null=True)

    def __str__(self):
        return self.content


class Attachment(models.Model):
    file = models.FileField(upload_to="ticket_attachments", blank=True, null=True)
    created_on = models.CharField(max_length=20, null=True)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, related_name="uploaded_by")
    parent_ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, null=True, related_name="attachment")
    def __str__(self):
        return self.file.name


