from django.urls import path

from . import views

urlpatterns = [
    path('users', views.getUserData),
    path('roles', views.getRoleData),
    path('tickets', views.getTicketData),
    path('comments', views.getCommentData),
    path('projects', views.getProjectData)

]
