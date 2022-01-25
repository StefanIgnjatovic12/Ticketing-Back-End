from django.shortcuts import render
from projects.forms import ProjectCreateForm
from django.contrib.auth.decorators import login_required
# Create your views here.

@login_required()
def create_project(request):
    if request.method == "POST":
        form = ProjectCreateForm(request.POST)
        if form.is_valid():
            form.save()
            title = form.cleaned_data.get('title')
            description = form.cleaned_data.get('description')
            assigned_user = form.cleaned_data.get('assigned_user')
        #   return redirect somewhere
        else:
            form = ProjectCreateForm()
        # return render something