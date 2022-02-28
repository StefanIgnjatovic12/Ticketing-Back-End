from django.db import models

from django.contrib.auth.models import User
# Create your models here.
class Role(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='roles')
    assigned_role = models.CharField(max_length=100)
