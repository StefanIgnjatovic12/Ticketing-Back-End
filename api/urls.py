from django.template.defaulttags import url
from django.urls import path, include, re_path
from knox import views as knox_views
import api.views
from . import views
from api.views import EditRoleData, UploadTicketAttachment, RegisterAPI, LoginAPI

urlpatterns = [
    path('password_reset/', include('django_rest_passwordreset.urls', namespace='password_reset')),
    path('register/', RegisterAPI.as_view(), name='register'),
    path('login/', LoginAPI.as_view(), name='login'),
    path('logout/', knox_views.LogoutView.as_view(), name='logout'),
    path('logoutall/', knox_views.LogoutAllView.as_view(), name='logoutall'),
    path('users/', views.getuserdata),
    path('roles/', views.getroledata),
    path('tickets/', views.getticketdata),
    path('comments/', views.getcommentdata),
    path('projects/', views.getprojectdata),

    path('users-update/<str:pk>/', views.edituserdata),
    path('users-delete/<str:pk>/', views.deleteuser),

    path('update-role/<str:pk>/', views.editoneroledata),
    path('update-role/', EditRoleData.as_view()),

    path('comment-update/<str:pk>/', views.editcommentdata),
    path('comment-delete/<str:pk>/', views.deletecomment),

    path('tickets/<str:pk>/', views.getticketdetails),
    path('ticket-update/<str:pk>/', views.editticketdata),
    path('ticket-delete/<str:pk>/', views.deleteticket),

    path('attachment-upload/', UploadTicketAttachment.as_view()),
    path('attachment-delete/<str:pk>', views.deleteattachment),

    path('projects/<str:pk>/', views.getprojectdetails),

    path('project-update/<str:pk>/', views.editprojectdata),
    path('project-delete/<str:pk>/', views.deleteproject),

    path('assigned-user-delete/projects/<str:projectId>/<str:userId>/', views.deleteassigneduser),
    path('assigned-ticket-delete/projects/<str:projectId>/<str:ticketId>/', views.deleteassignedticket),

]
