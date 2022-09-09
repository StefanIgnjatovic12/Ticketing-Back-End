from django.template.defaulttags import url
from django.urls import path, include, re_path
from knox import views as knox_views
import api.views
from . import views
from api.views import EditRoleData, UploadTicketAttachment, RegisterAPI, LoginAPI
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('password_reset/', include('django_rest_passwordreset.urls', namespace='password_reset')),
    path('register/', RegisterAPI.as_view(), name='register'),
    path('login/', LoginAPI.as_view(), name='login'),
    path('logout/', knox_views.LogoutView.as_view(), name='logout'),
    path('logoutall/', knox_views.LogoutAllView.as_view(), name='logoutall'),
    path('users/', views.get_user_data),
    path('roles/', views.get_role_data),
    path('tickets/', views.get_all_tickets),
    path('comments/', views.get_comment_data),
    path('projects/', views.get_project_data),

    path('users-update/<str:pk>/', views.edit_user_data),
    path('users-delete/<str:pk>/', views.delete_user),
    path('users-current/', views.get_current_user),
    path('project-users/<str:pk>', views.get_projects_assigned_to_user),
    path('developers-tickets-projects/<str:pk>/', views.get_tickets_and_projects_assigned_to_user),

    path('update-role/<str:pk>/', views.edit_one_role_data),
    path('update-role/', EditRoleData.as_view()),

    path('comment-create/', views.create_comment),
    path('comment-update/<str:pk>/', views.edit_comment_data),
    path('comment-delete/', views.delete_comment),

    path('tickets/<str:pk>/', views.get_ticket_details),
    path('ticket-create/', views.create_ticket),
    path('ticket-update/<str:pk>/', views.edit_ticket_data),
    path('ticket-delete/', views.delete_ticket),

    path('attachment-upload/', UploadTicketAttachment.as_view()),
    path('attachment-download/<str:pk>', views.download_attachment),
    path('attachment-delete/', views.delete_attachment),

    path('projects/<str:pk>/', views.get_project_details),
    path('project-create/', views.create_project),
    path('project-update/<str:pk>/', views.edit_project_data),
    path('project-delete/', views.delete_project),

    path('assigned-user-delete/projects/<str:projectId>/', views.remove_user_from_project),
    path('assigned-user-add/projects/', views.assign_user_to_project),
    path('assigned-user-add/tickets/', views.assign_user_to_ticket),

    path('dev-ticket-breakdown/<str:pk>/', views.get_ticket_count_for_user),
    path('all-ticket-breakdown/', views.get_ticket_count_all),

    path('search/', views.autocomplete_search)

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
