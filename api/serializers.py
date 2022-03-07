from rest_framework import serializers

from django.db import models
from django.contrib.auth.models import User
from Users.models import Role
from tickets.models import Ticket, Comment
from projects.models import Project


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['user', 'assigned_role']


class UserSerializer(serializers.ModelSerializer):
    roles = RoleSerializer(read_only=True, many=False)

    class Meta:
        model = User
        fields = '__all__'


class CommentSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True, many=False)

    class Meta:
        model = Comment
        fields = '__all__'


class TicketSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True, many=False)
    comments = CommentSerializer(read_only=True, many=True)


    class Meta:
        model = Ticket
        fields = '__all__'


class ProjectSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True, many=False)
    assigned_users = UserSerializer(read_only=True, many=True)
    assigned_tickets = TicketSerializer(read_only=True, many=True)

    class Meta:
        model = Project
        fields = '__all__'
