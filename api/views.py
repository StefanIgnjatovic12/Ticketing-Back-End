from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.db import models
from django.contrib.auth.models import User
from Users.models import Role
from tickets.models import Ticket, Comment
from projects.models import Project
from .serializers import UserSerializer, RoleSerializer, TicketSerializer, CommentSerializer, ProjectSerializer

# Get serialized objects of all the models in the project
@api_view(['GET'])
def getUserData(request):
    items = User.objects.all()
    serializer = UserSerializer(items, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def getRoleData(request):
    items = Role.objects.all()
    serializer = RoleSerializer(items, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def getCommentData(request):
    items = Comment.objects.all()
    serializer = CommentSerializer(items, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def getTicketData(request):
    items = Ticket.objects.all()
    serializer = TicketSerializer(items, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def getProjectData(request):
    items = Project.objects.all()
    serializer = ProjectSerializer(items, many=True)
    return Response(serializer.data)
