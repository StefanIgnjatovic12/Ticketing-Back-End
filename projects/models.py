from django.db import models
from tickets.models import Ticket
from django.utils import timezone
from django.conf import settings
from django.contrib.auth.models import User
from tickets.models import Ticket
# Create your models here.

class Project(models.Model):
    title = models.CharField(max_length=100, blank=False)
    description = models.TextField(default='', blank=False)
    created_on = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    assigned_users = models.ManyToManyField(User, related_name='assigned_users')
    assigned_tickets = models.ManyToManyField(Ticket)

    def __str__(self):
        return self.title