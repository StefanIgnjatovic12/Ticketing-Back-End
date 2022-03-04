from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

class Role(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='roles')
    assigned_role = models.CharField(max_length=100)


