from django.contrib import admin
from custom_user.admin import EmailUserAdmin
from .models import User, Tournament, Sponsor, Enrollment

# Register your models here.
admin.site.register(User)
admin.site.register(Tournament)
admin.site.register(Sponsor)
admin.site.register(Enrollment)
