from django.forms import ModelForm
from .models import Project
from django.utils.translation import gettext_lazy as _
# https://docs.djangoproject.com/en/4.0/ref/forms/fields/#django.forms.ModelMultipleChoiceField
# check above to see how many to many is mapped on the form
class ProjectCreateForm(ModelForm):
    class Meta:
        model = Project
        fields = ['title',
                  'description',
                  'assigned_user',
                  ]
        labels = {
            'title': _('Title'),
            'description': _('Description'),
            'assigned_user': _('Select users to assign to the project')
        }