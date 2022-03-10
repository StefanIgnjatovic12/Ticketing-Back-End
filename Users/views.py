# from django.shortcuts import render, redirect
# from django.contrib import messages
# from .forms import UserRegisterForm, UserUpdateForm
# from django.contrib.auth.decorators import login_required
# from .models import Role
# # Create your views here.
# def register(request):
#     if request.method == "POST":
#         form = UserRegisterForm(request.POST)
#         if form.is_valid():
#             form.save()
#             username = form.cleaned_data.get('username')
#             messages.success(request, f'Account created, you are now able to login')
#             return redirect('login')
#     else:
#         form = UserRegisterForm()
#     return render(request, 'users/register.html', {'form': form})

# @login_required
# def profile(request):
#     if request.method == "POST":
#         # if the request is POST, we populate the form with the data inputted in the form
#         u_form = UserUpdateForm(request.POST, instance=request.user)
#
#         if u_form.is_valid():
#             u_form.save()
#             messages.success(request, f'Update succesful')
#             return redirect('profile')
#     else:
#         # if the request isn't POST, we leave the current user info populated in the fields
#         u_form = UserUpdateForm(instance=request.user)
#     # context lets us use the forms on the profile.html file
#     context = {
#         'u_form':u_form,
#     }
#     return render(request, "users/profile.html", context)
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

