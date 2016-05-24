from django.contrib import admin
from custom_user.admin import EmailUserAdmin
from .models import PortalUser


class PortalUserAdmin(EmailUserAdmin):
    """
    You can customize the interface of your model here.
    """
    # pass

# Register your models here.
admin.site.register(PortalUser, PortalUserAdmin)
