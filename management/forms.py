from django import forms
from .models import Enrollment

class EnrollForm(forms.ModelForm):
    class Meta:
        model = Enrollment
        fields = ('ranking', 'license_id',)