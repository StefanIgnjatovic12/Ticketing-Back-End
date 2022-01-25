from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Role
# giving the ability to the admin to edit the role of a user from the parent user
# part in the admin panel
class RoleInLine(admin.StackedInline):
    model = Role
    can_delete = True

class UserAdmin(BaseUserAdmin):
    inlines = (RoleInLine,)

admin.site.unregister(User)
admin.site.register(User, UserAdmin)