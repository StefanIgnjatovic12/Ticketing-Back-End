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

# password reset
from django.core.mail import EmailMultiAlternatives
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.urls import reverse
from django_rest_passwordreset.signals import reset_password_token_created


# Register API
class RegisterAPI(generics.GenericAPIView):
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
            "user": UserSerializer(user, context=self.get_serializer_context()).data,
            "token": AuthToken.objects.create(user)[1]
        })


class LoginAPI(KnoxLoginView):
    authentication_classes = [BasicAuthentication]

    def get_post_response_data(self, request, token, instance):
        user = request.user
        data = {
            'expiry': self.format_expiry_datetime(instance.expiry),
            'token': token,
            'user': user.username,
            'role': user.roles.assigned_role

        }
        return data


# Password reset view > need to add user and password to settings
@receiver(reset_password_token_created)
def password_reset_token_created(sender, instance, reset_password_token, *args, **kwargs):
    context = {
        'current_user': reset_password_token.user,
        'username': reset_password_token.user.username,
        'email': reset_password_token.user.email,
        'reset_password_url': "{}?token={}".format(
            instance.request.build_absolute_uri(reverse('password_reset:reset-password-confirm')),
            reset_password_token.key)
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
        ['pythontesting85@gmail.com']
    )
    msg.attach_alternative(email_html_message, "text/html")
    # print(email_plaintext_message)
    msg.send()


@api_view(['GET'])
def getcurrentuser(request):
    user = request.user
    role = user.roles.assigned_role
    return Response({
        'user': user.username,
        'role': role
    })


@api_view(['GET'])
def getuserdata(request):
    items = User.objects.all()

    # enabling pagination because api_view doesn't have it by default
    paginator = LimitOffsetPagination()
    result_page = paginator.paginate_queryset(items, request)

    # creating 1 serializer instance for paginated and 1 for full
    serializer_page = UserSerializer(result_page, many=True)
    serializer_full = UserSerializer(items, many=True)

    # if limit is not specified, return all object data
    if 'limit' not in request.query_params:
        return Response(serializer_full.data)
    else:
        return Response(serializer_page.data)


@api_view(['POST'])
def edituserdata(request, pk):
    user = User.objects.get(id=pk)
    serializer = UserSerializer(instance=user, data=request.data)
    if serializer.is_valid():
        serializer.save()
    return Response(serializer.data)


@api_view(['DELETE'])
def deleteuser(request, pk):
    user = User.objects.get(id=pk)
    user.delete()
    return Response('Placeholder: user deleted')


# -----------------------------------------------

# Role object


@api_view(['GET'])
def getroledata(request):
    items = Role.objects.all()
    serializer = RoleSerializer(items, many=True)
    return Response(serializer.data)


# Update 1 role for 1 person
@api_view(['PUT'])
def editoneroledata(request, pk):
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
def getticketdata(request):
    items = Ticket.objects.all()
    serializer = TicketSerializer(items, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def getticketdetails(request, pk):
    ticket = Ticket.objects.get(id=pk)
    serializer = TicketSerializer(ticket)

    comment_list = []
    attachment_list = []
    ticket_changes = []

    ticket_author = {
        'user_id': serializer.data['id'],
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
        'created_by': f"{serializer.data['created_by']['first_name']} {serializer.data['created_by']['last_name']}",
        'parent_project': serializer.data['project']['title']
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
                'file_name': attachment['file'].split("/")[2],
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
        "ticket_history": ticket_changes[:4]
    }]
    # return Response(serializer.data)
    return Response(final_list)


@api_view(['PATCH'])
def editticketdata(request, pk):
    ticket = Ticket.objects.get(id=pk)
    serializer = TicketSerializer(instance=ticket, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()

    return Response(serializer.data)


@api_view(['POST'])
def createticket(request):
    user = User.objects.get(username=request.user)
    parent_project = int(request.data['parent_project'])
    created_on = request.data['created_on']
    title = request.data['ticket']['title']
    description = request.data['ticket']['description']
    priority = request.data['ticket']['priority']

    print([title, description, priority, created_on, parent_project, user])

    ticket = Ticket.objects.create(title=title,
                                   description=description,
                                   priority=priority,
                                   created_on=created_on,
                                   project_id=parent_project,
                                   created_by=user
                                   )

    return Response('Create ticket request went through')


@api_view(['DELETE'])
def deleteticket(request):
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
        if serializer.is_valid():
            serializer.validated_data['uploaded_by'] = user
            serializer.save()
            return Response(serializer.data['id'])
        else:

            return Response(serializer.errors)


@api_view(['GET'])
def downloadattachment(request, pk):
    obj = Attachment.objects.get(id=pk)
    filename = obj.file.path
    response = FileResponse(open(filename, 'rb'))
    response['Content-Disposition'] = f'attachment; filename={obj.file.name}'
    return response


@api_view(['DELETE'])
def deleteattachment(request):
    for attachmentID in request.data:
        attachment = Attachment.objects.get(id=attachmentID)
        attachment.delete()
    return Response('Placeholder: attachment deleted')


# -----------------------------------------------


# Comment object
@api_view(['GET'])
def getcommentdata(request):
    items = Comment.objects.all()
    serializer = CommentSerializer(items, many=True)
    return Response(serializer.data)


@api_view(['POST'])
def editcommentdata(request, pk):
    comment = Comment.objects.get(id=pk)

    serializer = CommentSerializer(instance=comment, data=request.data)
    if serializer.is_valid():
        serializer.save()
    return Response(serializer.data)


@api_view(['DELETE'])
def deletecomment(request):
    for id in request.data:
        comment = Comment.objects.get(id=id)
        comment.delete()
    return Response('Placeholder: comment deleted')


@api_view(['POST'])
def createcomment(request):
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
def getprojectdata(request):
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
def getprojectdetails(request, pk):
    project = Project.objects.get(id=pk)
    tickets = project.tickets.all()

    serializer = ProjectSerializer(project)

    user_list = []
    ticket_list = []
    final_list = []

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
                'created_by': f"{ticket.created_by.first_name} {ticket.created_by.last_name}"
            }
        )
        # ticket_list.append(ticket)

    final_list = [{

        'assigned_users': user_list,
        'assigned_tickets': ticket_list
    }]

    return Response(final_list)
    # return Response(serializer.data)


@api_view(['GET'])
def getprojectsassignedtouser(request, pk):
    user = User.objects.get(id=pk)
    # get list of projects to which the user is assigned
    project_list = user.assigned_users.all()
    project_ticket_dict = {}
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
        project_ticket_dict[f'{str(project)}'] = ticket_titles
    return Response(project_ticket_dict)


@api_view(['POST'])
def editprojectdata(request, pk):
    project = Project.objects.get(id=pk)
    serializer = ProjectSerializer(instance=project, data=request.data)
    if serializer.is_valid():
        serializer.save()
    return Response(serializer.data)


@api_view(['DELETE'])
def deleteproject(request):
    for projectID in request.data:
        project = Project.objects.get(id=projectID)
        project.delete()
    return Response('Placeholder: project deleted')


@api_view(['DELETE'])
def deleteassigneduser(request, projectId):
    # get Project
    project = Project.objects.get(id=projectId)
    print(request.data)
    # receive a list of user IDs from front end, loop through them
    for userID in request.data:
        user = project.assigned_users.get(id=userID)
        project.assigned_users.remove(user)

    return Response('User removed from project')

@api_view(['POST'])
def addassigneduser(request):
    data = request.data
    project = Project.objects.get(title=data['project'])
    user_id_list = data['user']
    # print(user_id_list)
    for id in user_id_list:
        user = User.objects.get(id=id)
        project.assigned_users.add(user)
    return Response('User added to project')
