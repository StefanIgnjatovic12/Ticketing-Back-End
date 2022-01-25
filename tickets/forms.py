from django.forms import ModelForm
from .models import Ticket, Comment
from django.utils.translation import gettext_lazy as _

class TicketCreateForm(ModelForm):
    class Meta:
        model = Ticket
        fields = [
            'title',
            'description',
            'priority'
        ]
        labels = {
            'title': _('Title'),
            'description': _('Description'),
            'priority': _('Select ticket priority')
        }

class CommentCreateForm(ModelForm):
    class Meta:
        model = Comment
        fields = [
            'content'
        ]