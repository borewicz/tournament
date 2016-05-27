from django import forms
from .models import Enrollment, Tournament


class EnrollForm(forms.ModelForm):
    class Meta:
        model = Enrollment
        fields = ('ranking', 'license_id',)


class TournamentForm(forms.ModelForm):
    class Meta:
        model = Tournament
        fields = ('name', 'description', 'deadline', 'date', 'longitude', 'latitude', 'limit', 'seeded_players',)
