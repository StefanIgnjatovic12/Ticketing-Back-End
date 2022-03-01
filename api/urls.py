from django.urls import path

import api.views
from . import views
from api.views import editRoleData


urlpatterns = [
    path('users/', views.getUserData),
    path('roles/', views.getRoleData),
    path('tickets/', views.getTicketData),
    path('comments/', views.getCommentData),
    path('projects/', views.getProjectData),

    path('users-update/<str:pk>/', views.editUserData),
    path('users-delete/<str:pk>/', views.deleteUser),

    path('update-role/<str:pk>/', views.editOneRoleData),
    path('update-role/', editRoleData.as_view()),

    path('comment-update/<str:pk>/', views.editCommentData),
    path('comment-delete/<str:pk>/', views.deleteComment),

    path('ticket-update/<str:pk>/', views.editTicketData),
    path('ticket-delete/<str:pk>/', views.deleteTicket),

    path('project-update/<str:pk>/', views.editProjectData),
    path('project-delete/<str:pk>/', views.deleteProject),

]
