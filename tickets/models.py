from django.db import models


from django.contrib.auth.models import User
from django.utils import timezone
from django.conf import settings
from django.urls import reverse
from simple_history.models import HistoricalRecords
from projects.models import Project


class Ticket(models.Model):
    PRIORITY_CHOICES = [
        ('Urgent', 'Urgent'),
        ('High', 'High'),
        ('Medium', 'Medium'),
        ('Low', 'Low')
    ]

    title = models.CharField(max_length=100, blank=True)
    description = models.TextField(default='', blank=True)
    created_on = models.CharField(max_length=20, null=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    priority = models.CharField(max_length=6, choices=PRIORITY_CHOICES, default='low')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tickets', null=True)
    history = HistoricalRecords()

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
    file = models.FileField(blank=True, null=True)
    created_on = models.CharField(max_length=20, null=True)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, related_name="uploaded_by")
    parent_ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, null=True, related_name="attachment")
    def __str__(self):
        return self.file.name


