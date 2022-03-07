from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.conf import settings
from django.urls import reverse


class Ticket(models.Model):
    PRIORITY_CHOICES = [
        ('Urgent', 'Urgent'),
        ('High', 'High'),
        ('Medium', 'Medium'),
        ('Low', 'Low')
    ]

    title = models.CharField(max_length=100, blank=False)
    description = models.TextField(default='', blank=False)
    created_on = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    priority = models.CharField(max_length=6, choices=PRIORITY_CHOICES, default='low')
    # assigned_comments = models.ForeignKey(Comment, on_delete=models.CASCADE, null=True, related_name='assigned_comments')

    def __str__(self):
        return self.title



class Comment(models.Model):
    content = models.TextField(default='', blank=False)
    parent_ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, null=True, related_name="comments")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_on = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.content

