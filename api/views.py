from django.contrib.auth.models import User
from rest_framework.decorators import api_view
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from django.core.exceptions import ValidationError
from rest_framework import status
from Users.models import Role
from projects.models import Project
from tickets.models import Ticket, Comment
from .serializers import UserSerializer, RoleSerializer, TicketSerializer, CommentSerializer, ProjectSerializer
from rest_framework.views import APIView


# Get serialized objects of all the models in the project

@api_view(['GET'])
def getUserData(request):
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
def editUserData(request, pk):
    user = User.objects.get(id=pk)
    serializer = UserSerializer(instance=user, data=request.data)
    if serializer.is_valid():
        serializer.save()
    return Response(serializer.data)


@api_view(['DELETE'])
def deleteUser(request, pk):
    user = User.objects.get(id=pk)
    user.delete()
    return Response('Placeholder: user deleted')


# -----------------------------------------------

# Role object


@api_view(['GET'])
def getRoleData(request):
    items = Role.objects.all()
    serializer = RoleSerializer(items, many=True)
    return Response(serializer.data)


# Update 1 role for 1 person
@api_view(['PUT'])
def editOneRoleData(request, pk):
    role = Role.objects.get(user_id=pk)
    serializer = RoleSerializer(instance=role, data=request.data)
    if serializer.is_valid():
        serializer.save()
    return Response(serializer.data)


# Update multiple roles at once
class editRoleData(APIView):
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
        print(data)
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
def getTicketData(request):
    items = Ticket.objects.all()
    serializer = TicketSerializer(items, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def getTicketDetails(request, pk):
    ticket = Ticket.objects.get(id=pk)
    serializer = TicketSerializer(ticket)

    final_list = []
    comment_list = []

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
                'created_by': f"{comment['created_by']['first_name']} {comment['created_by']['last_name']}"

            }
        )
    main_dict = {
        "ticket_author":ticket_author,
        "comments":comment_list,
        "ticket_info": ticket_info
    }
    final_list.append(main_dict)
    # return Response(serializer.data)
    return Response(final_list)


@api_view(['PUT'])
def editTicketData(request, pk):
    ticket = Ticket.objects.get(id=pk)
    serializer = TicketSerializer(instance=ticket, data=request.data)
    if serializer.is_valid():
        serializer.save()

    return Response(serializer.data)


@api_view(['DELETE'])
def deleteTicket(request, pk):
    ticket = Ticket.objects.get(id=pk)
    ticket.delete()
    return Response('Placeholder: ticket deleted')


# -----------------------------------------------

# Comment object
@api_view(['GET'])
def getCommentData(request):
    items = Comment.objects.all()
    serializer = CommentSerializer(items, many=True)
    return Response(serializer.data)


@api_view(['POST'])
def editCommentData(request, pk):
    comment = Comment.objects.get(id=pk)
    serializer = CommentSerializer(instance=comment, data=request.data)
    if serializer.is_valid():
        serializer.save()
    return Response(serializer.data)


@api_view(['DELETE'])
def deleteComment(request, pk):
    comment = Comment.objects.get(id=pk)
    comment.delete()
    return Response('Placeholder: comment deleted')


# -----------------------------------------------

# Project object

@api_view(['GET'])
def getProjectData(request):
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
def getProjectDetails(request, pk):
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
def editProjectData(request, pk):
    project = Project.objects.get(id=pk)
    serializer = ProjectSerializer(instance=project, data=request.data)
    if serializer.is_valid():
        serializer.save()
    return Response(serializer.data)


@api_view(['DELETE'])
def deleteProject(request, pk):
    project = Project.objects.get(id=pk)
    project.delete()
    return Response('Placeholder: project deleted')


@api_view(['DELETE'])
def deleteAssignedUser(request, projectId, userId):
    # get Project
    project = Project.objects.get(id=projectId)
    # get user from users assigned to specified project
    user = project.assigned_users.get(id=userId)

    # remove user from project without deleting the user object itself
    project.assigned_users.remove(user)

    return Response('User removed from project')


@api_view(['DELETE'])
def deleteAssignedTicket(request, projectId, ticketId):
    # get Project
    project = Project.objects.get(id=projectId)
    # get ticket from tickets assigned to specified project
    ticket = project.assigned_tickets.get(id=ticketId)

    # remove ticket from project without deleting the ticket object itself
    project.assigned_tickets.remove(ticket)

    return Response('Ticket removed from project')
