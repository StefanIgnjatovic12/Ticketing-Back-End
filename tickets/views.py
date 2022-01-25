from django.shortcuts import render
from .forms import TicketCreateForm, CommentCreateForm
from django.contrib.auth.decorators import login_required

@login_required()
def create_ticket (request):
    if request.method == 'POST':
        form = TicketCreateForm(request.POST)
        if form.is_valid():
            form.save()
            title = form.cleaned_data.get('title')
            description = form.cleaned_data.get('description')
            priority = form.cleaned_data.get('priority')
        #     return redirect something
        else:
            form = TicketCreateForm()
            # return return something

@login_required()
def create_comment(request):
    if request.method == 'POST':
        form = CommentCreateForm(request.POST)
        if form.is_valid():
            form.save()
            content = form.cleaned_data.get('content')
            #     return redirect something
        else:
            form = CommentCreateForm()
            #return render something