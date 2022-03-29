from rest_framework import serializers

from django.db import models
from django.contrib.auth.models import User
from Users.models import Role
from tickets.models import Ticket, Comment, Attachment
from projects.models import Project



class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['user', 'assigned_role']


class UserSerializer(serializers.ModelSerializer):
    roles = RoleSerializer(read_only=True, many=False)
    assigned_tickets = serializers.SerializerMethodField(method_name='get_assigned_tickets')
    assigned_projects = serializers.SerializerMethodField(method_name='get_assigned_projects')

    class Meta:
        model = User
        fields = '__all__'

    # methods to return the projects and tickets assigned to each user in the users endpoint

    def get_assigned_tickets(self, obj):
        # all query sets containing tickets grouped on which user they're assigned to
        all_query_sets = Ticket.objects.filter(assigned_developer=obj)
        final_ticket_list = []
        # if query set isn't empty
        if all_query_sets:
            # each query set can contain multiple tickets
            for tickets in all_query_sets:
                final_ticket_list.append(tickets.title)
        if len(final_ticket_list) > 0:
            return(final_ticket_list)

    def get_assigned_projects(self, obj):
        all_query_sets = obj.assigned_users.all()
        final_project_list = []
        if all_query_sets:
            for project in all_query_sets:
                final_project_list.append(project.title)
        if len(final_project_list) > 0:
            return(final_project_list)


# Register Serializer
class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'first_name', 'last_name')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(validated_data['username'],
                                        validated_data['email'],
                                        validated_data['password'],
                                        first_name=validated_data['first_name'],
                                        last_name=validated_data['last_name'])

        return user
class CommentSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True, many=False)

    class Meta:
        model = Comment
        fields = '__all__'

class AttachmentSerialiazer(serializers.ModelSerializer):
    uploaded_by = UserSerializer(read_only=True, many=False)

    class Meta:
        model = Attachment
        fields = '__all__'



class ProjectSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True, many=False)
    assigned_users = UserSerializer(read_only=True, many=True)


    class Meta:
        model = Project
        fields = '__all__'

class TicketSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True, many=False)
    changed_by = UserSerializer(read_only=True, many=False)
    comments = CommentSerializer(read_only=True, many=True)
    attachment = AttachmentSerialiazer(read_only=True, many=True)
    project = ProjectSerializer(read_only=True, many=False)
    assigned_developer = UserSerializer(read_only=True, many=False)
    class Meta:
        model = Ticket
        fields = '__all__'


class SimpleTicketSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ticket
        fields = ['title']
