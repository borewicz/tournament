from django import forms
from .models import Enrollment, Tournament, Sponsor, Match
from bootstrap3_datetime.widgets import DateTimePicker
from datetime import date
from django.utils import timezone


class EnrollForm(forms.ModelForm):
    class Meta:
        model = Enrollment
        fields = ('ranking', 'license_id',)


class TournamentForm(forms.ModelForm):
    sponsors = forms.ModelMultipleChoiceField(queryset=Sponsor.objects.all(),
                                              required=False,
                                              widget=forms.CheckboxSelectMultiple)

    class Meta:
        model = Tournament
        # fields = ('name', 'description', 'deadline', 'date', 'longitude', 'latitude', 'limit', 'seeded_players', '')
        exclude = ['organizer']
        widgets = {
            'date': DateTimePicker(options={"format": "YYYY-MM-DD HH:mm",
                                            "pickSeconds": False}),
            'deadline': DateTimePicker(options={"format": "YYYY-MM-DD HH:mm",
                                                "pickSeconds": False})
        }

    def clean(self):
        cleaned_data = super(TournamentForm, self).clean()
        form_date = cleaned_data.get("date")
        if timezone.now() > form_date:
            self.add_error('date', "You cannot add tournament from past.")

        if cleaned_data.get("deadline") > form_date:
            self.add_error('deadline', "Deadline must start later than start date.")


class MatchForm(forms.ModelForm):
    class Meta:
        model = Match
        fields = ('score',)
