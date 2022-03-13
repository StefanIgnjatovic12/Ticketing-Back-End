from django.contrib.auth.models import User
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
import json
from django.core.exceptions import ValidationError
from rest_framework import status, generics, permissions
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

                          )
from rest_framework.views import APIView
from rest_framework.response import Response
import datetime
# knox
from knox.models import AuthToken
from knox.views import LoginView as KnoxLoginView
from rest_framework.authtoken.serializers import AuthTokenSerializer
from django.contrib.auth import login
from rest_framework.authentication import BasicAuthentication

# password reset
from django.core.mail import EmailMultiAlternatives
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.urls import reverse
from django_rest_passwordreset.signals import reset_password_token_created
from rest_framework.renderers import JSONRenderer


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

    final_list = []
    comment_list = []
    attachment_list = []

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
        'priority': serializer.data['priority']
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

            }
        )
    main_dict = {
        "ticket_author": ticket_author,
        "comments": comment_list,
        "ticket_info": ticket_info,
        "attachments": attachment_list
    }
    final_list.append(main_dict)
    # return Response(serializer.data)
    return Response(final_list)


@api_view(['PUT'])
def editticketdata(request, pk):
    ticket = Ticket.objects.get(id=pk)
    serializer = TicketSerializer(instance=ticket, data=request.data)
    if serializer.is_valid():
        serializer.save()

    return Response(serializer.data)


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
        file = request.data
        print(file)
        serializer = AttachmentSerialiazer(data=file)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data['id'])
        else:

            return Response(serializer.errors)


@api_view(['DELETE'])
def deleteattachment(request, pk):
    attachment = Attachment.objects.get(id=pk)
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
    created_on = "2022-03-05T16:50:18Z"
    print(content, parent_ticket)
    comment = Comment.objects.create(content=content,
                                     parent_ticket=parent_ticket,
                                     created_by=user,
                                     created_on=created_on)
    print(comment)
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
    for ticket in serializer.data['assigned_tickets']:
        ticket_list.append(
            {
                'title': ticket['title'],
                'description': ticket['description'],
                'priority': ticket['priority'],
                'id': ticket['id'],
                'created_by': f"{ticket['created_by']['first_name']} {ticket['created_by']['last_name']}"
            }
        )
        # ticket_list.append(ticket)

    main_dict = {

        'assigned_users': user_list,
        'assigned_tickets': ticket_list
    }

    final_list.append(main_dict)
    return Response(final_list)
    # return Response(serializer.data)


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

    # receive a list of user IDs from front end, loop through them
    for userID in request.data:
        user = project.assigned_users.get(id=userID)
        project.assigned_users.remove(user)

    return Response('User removed from project')



