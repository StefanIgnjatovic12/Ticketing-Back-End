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

# User object
# @api_view(['GET'])
# def getUserData(request):
#     items = User.objects.all()
#     serializer = UserSerializer(items, many=True)
#     return Response(serializer.data)
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
    print(role.assigned_role)
    print(request.data)
    print(serializer.data)
    print(role.assigned_role)
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


@api_view(['POST'])
def editTicketData(request, pk):
    comment = Ticket.objects.get(id=pk)
    serializer = TicketSerializer(instance=comment, data=request.data)
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
def getAssignedPersonnel(request, pk):
    project = Project.objects.get(id=pk)
    serializer = ProjectSerializer(project)
    user_list = []
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
    return Response(user_list)


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
