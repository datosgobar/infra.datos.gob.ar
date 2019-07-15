from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from infra.apps.users.models import User

admin.site.register(User, UserAdmin)
