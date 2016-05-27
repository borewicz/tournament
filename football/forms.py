from django import forms
from .models import Enrollment, User

class EnrollForm(forms.ModelForm):
    class Meta:
        model = Enrollment
        fields = ('ranking', 'license_id',)


# class CustomEmailRegistrationForm(EmailRegistrationForm):
#     first_name = forms.CharField()
#     last_name = forms.CharField()

