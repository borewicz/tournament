from django.contrib import admin
# from custom_user.admin import EmailUserAdmin
from .models import *
# from .forms import UserCreationForm

'''
class UserAdmin(EmailUserAdmin):
    model = User
    add_form = UserCreationForm
    fieldsets = EmailUserAdmin.fieldsets + (
        (None, {'fields': ('name', 'surname',)}),
    )
    pass
'''

# Register your models here.
admin.site.register(User)
# admin.site.register(User, UserAdmin)
admin.site.register(Tournament)
admin.site.register(Sponsor)
admin.site.register(Enrollment)
admin.site.register(Match)
admin.site.register(Round)