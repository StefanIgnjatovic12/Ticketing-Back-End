from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.db import models
from django.contrib.auth.models import User
from Users.models import Role
from tickets.models import Ticket, Comment
from projects.models import Project
from .serializers import UserSerializer, RoleSerializer, TicketSerializer, CommentSerializer, ProjectSerializer

# Get serialized objects of all the models in the project

# User object
@api_view(['GET'])
def getUserData(request):
    items = User.objects.all()
    serializer = UserSerializer(items, many=True)
    return Response(serializer.data)

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

@api_view(['POST'])
def editRoleData(request, pk):
    role = Role.objects.get(id=pk)
    serializer = RoleSerializer(instance=role, data=request.data)
    if serializer.is_valid():
        serializer.save()
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
    serializer = ProjectSerializer(items, many=True)
    return Response(serializer.data)

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