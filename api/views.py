import boto3
from django.contrib.auth.models import User
from rest_framework.decorators import api_view
from datetime import datetime
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.parsers import MultiPartParser, FormParser
from django.core.exceptions import ValidationError
from rest_framework import status, generics
from Users.models import Role
from projects.models import Project
from tickets.models import Ticket, Comment, Attachment
from .serializers import (AttachmentSerialiazer,
                          UserSerializer,
                          RoleSerializer,
                          TicketSerializer,
                          CommentSerializer,
                          ProjectSerializer,
                          RegisterSerializer,
                          SimpleTicketSerializer

                          )
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import FileResponse
# knox
from knox.models import AuthToken
from knox.views import LoginView as KnoxLoginView
from django.http import JsonResponse

from rest_framework.authentication import BasicAuthentication
import uuid
from Ticketing_system_and_issue_tracker.settings import AWS_SECRET_ACCESS_KEY, AWS_ACCESS_KEY_ID
from smart_open import open as smart_opener

# password reset
from django.core.mail import EmailMultiAlternatives
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.urls import reverse
from django_rest_passwordreset.signals import reset_password_token_created
import requests
import json
import re
# Register API
class RegisterAPI(generics.GenericAPIView):
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # assign user the "User" role upon registering
        user_id = UserSerializer(user, context=self.get_serializer_context()).data['id']
        user_object = User.objects.get(id=user_id)
        role = Role.objects.create(user_id=user_id, assigned_role='User')
        user_object.save()
        return Response({
            "user": UserSerializer(user, context=self.get_serializer_context()).data,
            "token": AuthToken.objects.create(user)[1]
        })


# prevents the basic auth popup on incorrect login info
class BasicLikeAuthentication(BasicAuthentication):
    def authenticate_header(self, request):
        return f'BasicLike realm="{self.www_authenticate_realm}"'


class LoginAPI(KnoxLoginView):
    authentication_classes = [BasicLikeAuthentication]

    def get_post_response_data(self, request, token, instance):
        user = request.user
        data = {
            'expiry': self.format_expiry_datetime(instance.expiry),
            'token': token,
            'user': user.username,
            'role': user.roles.assigned_role

        }
        return data

@api_view(['POST'])
def demo_account_signin(request):
    params = {'username': 'Test', 'password': 'gofastmen12'}
    r = requests.post('https://drf-react-ticketing-backend.herokuapp.com/api/login/', json=params)
    if r.status_code == 200:
        response_dict = json.loads(r.text)
        return Response({'token': response_dict['access_token']})
    print('Failed demo login reasons:')
    print(r.status_code)
    print(r.reason)
    return Response('Could not save data')

# Password reset view > need to add user and password to settings
@receiver(reset_password_token_created)
def password_reset_token_created(sender, instance, reset_password_token, *args, **kwargs):
    context = {
        'current_user': reset_password_token.user,
        'username': reset_password_token.user.username,
        'email': reset_password_token.user.email,
        'reset_password_url': "{}?token={}".format(
            instance.request.build_absolute_uri(reverse('password_reset:reset-password-confirm')),
            reset_password_token.key),
        'react_reset_url': f"http://drf-react-ticketing-frontend/password-reset/{reset_password_token.key}"
    }

    # render email text
    email_html_message = render_to_string('email/user_reset_password.html', context)
    email_plaintext_message = render_to_string('email/user_reset_password.txt', context)

    msg = EmailMultiAlternatives(
        # title:
        "Password Reset for {title}".format(title="Some website title"),
        # message:
        email_plaintext_message,
        # from:
        "pythontesting85@gmail.com",
        # to:
        [reset_password_token.user.email]
    )
    msg.attach_alternative(email_html_message, "text/html")
    # print(email_plaintext_message)
    msg.send()
    return Response('Password reset')


@api_view(['GET'])
def get_current_user(request):
    user = request.user
    role = user.roles.assigned_role
    return Response([{
        'user': user.username,
        'role': role,
        'id': user.id
    }])


@api_view(['GET'])
def get_user_data(request):
    users = User.objects.all()

    # enabling pagination because api_view doesn't have it by default
    paginator = LimitOffsetPagination()
    result_page = paginator.paginate_queryset(users, request)

    # creating 1 serializer instance for paginated and 1 for full
    serializer_page = UserSerializer(result_page, many=True)
    serializer_full = UserSerializer(users, many=True)
    # for user in users:
    #     print(user.assigned_developer.all())
    # if limit is not specified, return all object data
    if 'limit' not in request.query_params:
        return Response(serializer_full.data)
    else:
        return Response(serializer_page.data)


@api_view(['POST'])
def edit_user_data(request, pk):
    user = User.objects.get(id=pk)
    serializer = UserSerializer(instance=user, data=request.data)
    if serializer.is_valid():
        serializer.save()
    return Response(serializer.data)


@api_view(['DELETE'])
def delete_user(request, pk):
    user = User.objects.get(id=pk)
    user.delete()
    return Response('Placeholder: user deleted')


# -----------------------------------------------

# Role object


@api_view(['GET'])
def get_role_data(request):
    items = Role.objects.all()
    serializer = RoleSerializer(items, many=True)
    return Response(serializer.data)


# Update 1 role for 1 person
@api_view(['PUT'])
def edit_one_role_data(request, pk):

    role = Role.objects.get(user_id=pk)
    serializer = RoleSerializer(instance=role, data=request.data)
    if serializer.is_valid():
        serializer.save()
    return Response(serializer.data)


# Update multiple roles at once
class EditRoleData(APIView):
    def get_object(self, obj_id):
        try:
            return Role.objects.get(user=obj_id)
        except (Role.DoesNotExist, ValidationError):
            raise status.HTTP_400_BAD_REQUEST

    def validate_ids(self, id_list):
        for id in id_list:
            try:
                Role.objects.get(user=id)
            except (Role.DoesNotExist, ValidationError):
                raise status.HTTP_400_BAD_REQUEST
        return True

    def put(self, request, *args, **kwargs):
        data = request.data
        user_ids = [i['user'] for i in data]
        self.validate_ids(user_ids)
        instances = []
        for temp_dict in data:
            user = temp_dict['user']
            assigned_role = temp_dict['assigned_role']
            obj = self.get_object(user)
            obj.assigned_role = assigned_role
            obj.save()
            instances.append(obj)
        serializer = RoleSerializer(instances, many=True)
        return Response(serializer.data)


# -----------------------------------------------

# Ticket object
@api_view(['GET'])
def get_all_tickets(request):
    items = Ticket.objects.all()
    serializer = TicketSerializer(items, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def get_ticket_details(request, pk):
    ticket = Ticket.objects.get(id=pk)
    serializer = TicketSerializer(ticket)
    comment_list = []
    attachment_list = []
    ticket_changes = []
    if serializer.data['assigned_developer'] is not None:
        assigned_developer = f"{serializer.data['assigned_developer']['first_name']} {serializer.data['assigned_developer']['last_name']}"
    else:
        assigned_developer = 'Unassigned'
    ticket_author = {
        'user_id': serializer.data['created_by']['id'],
        'username': serializer.data['created_by']['username'],
        'first_name': serializer.data['created_by']['first_name'],
        'last_name': serializer.data['created_by']['last_name'],
        'email': serializer.data['created_by']['email'],
    }

    ticket_info = {
        'title': serializer.data['title'],
        'description': serializer.data['description'],
        'created_on': serializer.data['created_on'],
        'priority': serializer.data['priority'],
        'update_time': serializer.data['update_time'],
        'created_by': f"{serializer.data['created_by']['first_name']} {serializer.data['created_by']['last_name']}",\
        'created_by_id': serializer.data['created_by']['id'],
        'parent_project': serializer.data['project']['title'],
        'assigned_developer': assigned_developer,
        'assigned_developer_id': serializer.data['assigned_developer']['id'],
        'status': serializer.data['status'],
        'type': serializer.data['type']
    }

    for comment in serializer.data['comments']:
        comment_list.append(
            {
                'content': comment['content'],
                'created_on': comment['created_on'],
                'created_by': f"{comment['created_by']['first_name']} {comment['created_by']['last_name']}",
                'id': comment['id']
            }
        )
    for attachment in serializer.data['attachment']:
        attachment_list.append(
            {
                # 'file_name': attachment['file'].split("/")[2],
                'file_name': re.search('ticket_attachments/(.*)\?', attachment['file']).group(1),
                'uploaded_by': f"{attachment['uploaded_by']['first_name']} {attachment['uploaded_by']['last_name']}",
                'created_on': attachment['created_on'],
                'id': attachment['id']
            }
        )
    # loops through the history table and logs the differences/edits
    # update_time = datetime.now().strftime("%d/%m/%Y %R")
    for current_edit in ticket.history.all()[:4]:
        previous_edit = current_edit.prev_record
        if current_edit and previous_edit is not None:
            delta = current_edit.diff_against(previous_edit)
            for change in delta.changes[:3]:
                ticket_changes.append(
                    {
                        'changed_field': change.field,
                        'old_value': change.old,
                        'new_value': change.new,

                    }
                )

    final_list = [{
        "ticket_author": ticket_author,
        "comments": comment_list,
        "ticket_info": ticket_info,
        "attachments": attachment_list,
        "ticket_history": ticket_changes[:4],

    }]
    # return Response(serializer.data)
    return Response(final_list)

# used for individual user dashboards
@api_view(['GET'])
def get_tickets_and_projects_assigned_to_user(request, pk):
    user = User.objects.get(id=pk)

    if user.roles.assigned_role =='Admin' or user.roles.assigned_role == 'Developer':
        ticket_query_set = user.assigned_developer.all()

    elif user.roles.assigned_role == 'User':
        ticket_query_set = Ticket.objects.filter(created_by=user)

    project_query_set = user.assigned_users.all()

    ticket_list = []
    project_list = []
    for ticket in ticket_query_set:
        serialized = TicketSerializer(ticket).data
        ticket_dict = {
            "title": serialized['title'],
            "description": serialized['description'],
            "created_by": f"{serialized['created_by']['first_name']} {serialized['created_by']['last_name']}",
            "created_on": serialized['created_on'],
            "priority": serialized['priority'],
            "type": serialized['type'],
            "id": serialized['id']
        }
        ticket_list.append(ticket_dict)
    for project in project_query_set:
        serialized = ProjectSerializer(project).data
        project_dict = {
            "title": serialized['title'],
            "description": serialized['description'],
            "created_by": f"{serialized['created_by']['first_name']} {serialized['created_by']['last_name']}",
            "created_on": serialized['created_on'],
            "id": serialized['id']
        }
        project_list.append(project_dict)
    final_dict = {
        "projects": project_list,
        "tickets": ticket_list
    }
    return Response([final_dict])

@api_view(['GET'])
# view to show number of tickets by type, priority and status on home page for dev
def get_ticket_count_for_user(request, pk):
    ticket_type_choices = ['Bug report', 'Feature request', 'Not specified', 'Other']
    ticket_priority_choices = ['Urgent', 'High', 'Medium', 'Low']
    ticket_status_choices = ['Assigned/In progress', 'Resolved']

    user = User.objects.get(id=pk)
    ticket_query_set = user.assigned_developer.all()
    ticket_type_list = []
    ticket_priority_list = []
    ticket_status_list = []

    ticket_type_dict = {}
    ticket_priority_dict = {}
    ticket_status_dict = {}


    for ticket in ticket_query_set:
        serialized = TicketSerializer(ticket).data
        ticket_type_list.append(serialized['type'])
        ticket_status_list.append(serialized['status'])
        ticket_priority_list.append(serialized['priority'])

    for choice in ticket_type_choices:
        ticket_type_dict[choice] = ticket_type_list.count(choice)

    for choice in ticket_priority_choices:
        ticket_priority_dict[choice] = ticket_priority_list.count(choice)

    for choice in ticket_status_choices:
        ticket_status_dict[choice] = ticket_status_list.count(choice)

    final_dict = {
        'tickets_by_type': ticket_type_dict,
        'tickets_by_priority': ticket_priority_dict,
        'tickets_by_status': ticket_status_dict
    }
    return Response (final_dict)

@api_view(['GET'])
# view to show number of tickets by type, priority and status on home page for dev
def get_ticket_count_all(request):
    ticket_type_choices = ['Bug report', 'Feature request', 'Not specified', 'Other']
    ticket_priority_choices = ['Urgent', 'High', 'Medium', 'Low']
    ticket_status_choices = ['Assigned/In progress', 'Resolved']

    ticket_query_set = Ticket.objects.all()
    ticket_type_list = []
    ticket_priority_list = []
    ticket_status_list = []

    ticket_type_dict = {}
    ticket_priority_dict = {}
    ticket_status_dict = {}


    for ticket in ticket_query_set:
        serialized = TicketSerializer(ticket).data
        ticket_type_list.append(serialized['type'])
        ticket_status_list.append(serialized['status'])
        ticket_priority_list.append(serialized['priority'])

    for choice in ticket_type_choices:
        ticket_type_dict[choice] = ticket_type_list.count(choice)

    for choice in ticket_priority_choices:
        ticket_priority_dict[choice] = ticket_priority_list.count(choice)

    for choice in ticket_status_choices:
        ticket_status_dict[choice] = ticket_status_list.count(choice)

    final_dict = {
        'tickets_by_type': ticket_type_dict,
        'tickets_by_priority': ticket_priority_dict,
        'tickets_by_status': ticket_status_dict
    }
    return Response (final_dict)

@api_view(['PATCH'])
def edit_ticket_data(request, pk):
    ticket = Ticket.objects.get(id=pk)
    serializer = TicketSerializer(instance=ticket, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()

    return Response(serializer.data)


@api_view(['POST'])
def create_ticket(request):
    user = User.objects.get(username=request.user)
    parent_project = int(request.data['parent_project'])
    created_on = request.data['created_on']
    title = request.data['ticket']['title']
    description = request.data['ticket']['description']
    priority = request.data['ticket']['priority']
    type = request.data['ticket']['type']

    ticket = Ticket.objects.create(title=title,
                                   description=description,
                                   priority=priority,
                                   created_on=created_on,
                                   project_id=parent_project,
                                   created_by=user,
                                   type=type
                                   )

    return Response('Create ticket request went through')


@api_view(['POST'])
def assign_user_to_ticket(request):
    data = request.data

    ticket = Ticket.objects.get(title=data['ticket'])
    user_id = data['user']
    user = User.objects.get(id=user_id[0])
    if ticket.assigned_developer == user:
        return Response('Ticket already assigned to user')
    elif user.roles.assigned_role == 'User':
        return Response('Tickets can only be assigned to developers or admins')
    ticket.assigned_developer = user
    ticket.status = 'Assigned/In progress'
    ticket.save()
    return Response('User assigned to ticket')


@api_view(['DELETE'])
def delete_ticket(request):
    for ticketID in request.data:
        ticket = Ticket.objects.get(id=ticketID)
        ticket.delete()
    return Response('Placeholder: ticket deleted')


class UploadTicketAttachment(APIView):
    permission_classes = []
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, format=None):
        user = request.user
        serializer = AttachmentSerialiazer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.validated_data['uploaded_by'] = user
            serializer.save()
            return Response(serializer.data['id'])
        else:
            return Response(f'{serializer.errors}, attachment upload failed')


@api_view(['GET'])
def download_attachment(request, pk):
    session = boto3.Session(aws_access_key_id=AWS_ACCESS_KEY_ID,
                            aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
    obj = Attachment.objects.get(id=pk)
    with smart_opener(f's3://bucketeer-0f6cb5f5-34a1-49a1-ab57-f884d7245601/bucketeer-0f6cb5f5-34a1-49a1-ab57'
                      f'-f884d7245601/media/public/{str(obj)}',
                      "rb",
                      transport_params={
                          'client':
                              session.client(
                                  's3')}) \
            as attachment:
        response = FileResponse(open(attachment.read(), 'rb'))
    response['Content-Disposition'] = f'attachment; filename={obj.file.name}'
    return response


@api_view(['DELETE'])
def delete_attachment(request):
    for attachmentID in request.data:
        attachment = Attachment.objects.get(id=attachmentID)
        attachment.delete()
    return Response('Placeholder: attachment deleted')


# -----------------------------------------------


# Comment object
@api_view(['GET'])
def get_comment_data(request):
    items = Comment.objects.all()
    serializer = CommentSerializer(items, many=True)
    return Response(serializer.data)


@api_view(['POST'])
def edit_comment_data(request, pk):
    comment = Comment.objects.get(id=pk)

    serializer = CommentSerializer(instance=comment, data=request.data)
    if serializer.is_valid():
        serializer.save()
    return Response(serializer.data)


@api_view(['DELETE'])
def delete_comment(request):
    for id in request.data:
        comment = Comment.objects.get(id=id)
        comment.delete()
    return Response('Placeholder: comment deleted')


@api_view(['POST'])
def create_comment(request):
    user = User.objects.get(username=request.user)
    parent_ticket = Ticket.objects.get(id=int(request.data['parent_ticket']))
    content = request.data['comment']
    created_on = request.data['created_on']

    comment = Comment.objects.create(content=content,
                                     parent_ticket=parent_ticket,
                                     created_by=user,
                                     created_on=created_on)
    return Response('Create comment request went through')


# -----------------------------------------------

# Project object

@api_view(['GET'])
def get_project_data(request):
    items = Project.objects.all()

    paginator = LimitOffsetPagination()
    result_page = paginator.paginate_queryset(items, request)

    serializer_page = ProjectSerializer(result_page, many=True)
    serializer_full = ProjectSerializer(items, many=True)

    if 'limit' not in request.query_params:
        return Response(serializer_full.data)
    else:
        return Response(serializer_page.data)


@api_view(['GET'])
def get_project_details(request, pk):
    project = Project.objects.get(id=pk)
    tickets = project.tickets.all()

    serializer = ProjectSerializer(project)

    project_info = {
        'title': serializer.data['title'],
        'description': serializer.data['description'],
        'created_by': f"{serializer.data['created_by']['first_name']} {serializer.data['created_by']['last_name']}",
        'created_by_id': serializer.data['created_by']['id'],
        'created_on': serializer.data['created_on'],
        'id': serializer.data['id']

    }

    user_list = []
    ticket_list = []

    # loops over users assigned to project and adds 1 dictionary per user to the user_list
    for user in serializer.data['assigned_users']:
        user_list.append(
            {
                'user_id': user['id'],
                'assigned_role': user['roles']['assigned_role'],
                'username': user['username'],
                'first_name': user['first_name'],
                'last_name': user['last_name'],
                'email': user['email'],
            }
        )

    # loops over the tickets assigned to a project and adds them to the ticket list
    for ticket in tickets:
        ticket_list.append(
            {
                'title': ticket.title,
                'description': ticket.description,
                'priority': ticket.priority,
                'id': ticket.id,
                'created_by': f"{ticket.created_by.first_name} {ticket.created_by.last_name}",
                # 'type': ticket.type,
                # 'status': ticket.status
            }
        )
        # ticket_list.append(ticket)

    final_list = [{

        'assigned_users': user_list,
        'assigned_tickets': ticket_list,
        'project_info': project_info
    }]

    return Response(final_list)
    # return Response(serializer.data)


@api_view(['GET'])
def get_projects_assigned_to_user(request, pk):
    user = User.objects.get(id=pk)
    # get list of projects to which the user is assigned
    project_list = user.assigned_users.all()
    project_ticket_list = []
    # Loop through list of projects
    for project in project_list:
        # Get tickets assigned to each project
        assigned_tickets = project.tickets.all()
        ticket_titles = []
        # loop through tickets assigned to the project
        for ticket in assigned_tickets:
            # serialize each ticket and get its title in a dictionary
            serialized = SimpleTicketSerializer(instance=ticket).data
            # append only the title string to the list
            ticket_titles.append(serialized['title'])

        # add project and it's corresponding tickets to dictionary
        project_ticket_list.append(
            {
                'project': str(project),
                'tickets': ticket_titles
                # f'{str(project)}' : ticket_titles
            }
        )

    return Response(project_ticket_list)


@api_view(['PATCH'])
def edit_project_data(request, pk):
    project = Project.objects.get(id=pk)
    serializer = ProjectSerializer(instance=project, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
    return Response(serializer.data)


@api_view(['DELETE'])
def delete_project(request):
    for projectID in request.data:
        project = Project.objects.get(id=projectID)
        project.delete()
    return Response('Placeholder: project deleted')


@api_view(['DELETE'])
def remove_user_from_project(request, projectId):
    # get Project
    project = Project.objects.get(id=projectId)
    # receive a list of user IDs from front end, loop through them
    for userID in request.data:
        user = project.assigned_users.get(id=userID)
        project.assigned_users.remove(user)

    return Response('User removed from project')


@api_view(['POST'])
def assign_user_to_project(request):
    data = request.data
    project = Project.objects.get(title=data['project'])
    user_id_list = data['user']
    for id in user_id_list:
        user = User.objects.get(id=id)
        if user in project.assigned_users.all():
            return Response('User already assigned to project')
        project.assigned_users.add(user)
    return Response('User added to project')


@api_view(['POST'])
def create_project(request):
    user = User.objects.get(username=request.user)
    title = request.data['project']['title']
    description = request.data['project']['description']
    created_on = request.data['created_on']
    users_to_assign_list = request.data['selected_users']
    project = Project.objects.create(title=title,
                                     description=description,
                                     created_on=created_on,
                                     created_by=user)

    project.assigned_users.set(users_to_assign_list)
    return Response('Project created')

# _________________AUTOCOMPLETE SEARCH______________
@api_view(['GET'])
def autocomplete_search(request):
    ticket_query_set = Ticket.objects.all()
    project_query_set = Project.objects.all()
    user_query_set = User.objects.all()
    response_list = []
    for project in project_query_set:
        response_list.append(
            {
                'title': project.title,
                'id': project.id,
                'type': 'Projects',
                'key': uuid.uuid4()
             }
        )
    for ticket in ticket_query_set:
        response_list.append(
            {
                'title': ticket.title,
                'id': ticket.id,
                'type': 'Tickets',
                'key': uuid.uuid4()
             }
        )
    for user in user_query_set:
        response_list.append(
            {
                'title': user.username,
                'id': user.id,
                'type': 'Users',
                'key': uuid.uuid4()
            }
        )
    return Response(response_list)
