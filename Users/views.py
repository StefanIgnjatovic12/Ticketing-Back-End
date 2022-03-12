# from django.shortcuts import render, redirect
# from django.contrib import messages
# from .forms import UserRegisterForm, UserUpdateForm
# from django.contrib.auth.decorators import login_required
# from .models import Role

#
# # https://docs.djangoproject.com/en/4.0/topics/auth/default/
# #  use the default permissions to let users add, change, view and delete
# # might go into different app
# def role_permissions(request):
#     current_user = request.user
#     if current_user.role.assigned_role == "Developer":
#         # if ticket is assigned to developer dev has permission to
#         # change ticket state
#         pass
#     elif current_user.role.assigned_role == "Submitter":
#         # if comment was made by submitter he can edit/delete it
#         pass
#     elif current_user.role.assigned_role== "Project manager":
#         # if project is assigned to project manager he can assign users/devs to ticket
#
#         pass

