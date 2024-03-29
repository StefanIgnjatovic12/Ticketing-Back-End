from django.db import models
# from tickets.models import Ticket
from django.utils import timezone
from django.conf import settings
from django.contrib.auth.models import User
# Create your models here.

class Project(models.Model):
    title = models.CharField(max_length=100, blank=False)
    description = models.TextField(default='', blank=False)
    created_on = models.CharField(max_length=20, null=True)
    # https://stackoverflow.com/questions/34305805/foreignkey-user-in-models
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_by')
    assigned_users = models.ManyToManyField(User, related_name='assigned_users', blank=True)

    def __str__(self):
        return self.title