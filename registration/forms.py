"""
Forms and validation code for user registration.

Note that all of these forms assume your user model is similar in
structure to Django's default User class. If your user model is
significantly different, you may need to write your own form class;
see the documentation for notes on custom user models with
django-registration.

"""

from django import forms
from django.contrib.auth import get_user_model
from custom_user.forms import EmailUserCreationForm
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from . import validators

User = get_user_model()


class RegistrationForm(EmailUserCreationForm):
    class Meta(EmailUserCreationForm.Meta):
        fields = [
            User.USERNAME_FIELD,
            'first_name',
            'last_name',
            'team',
            'password1',
            'password2'
        ]
        required_css_class = 'required'

    def clean(self):
        username_value = self.cleaned_data.get(User.USERNAME_FIELD)
        if username_value is not None:
            try:
                if hasattr(self, 'reserved_names'):
                    reserved_names = self.reserved_names
                else:
                    reserved_names = validators.DEFAULT_RESERVED_NAMES
                validator = validators.ReservedNameValidator(
                    reserved_names=reserved_names
                )
                validator(username_value)
            except ValidationError as v:
                self.add_error(User.USERNAME_FIELD, v)

    def save(self, commit=True):
        user = super(RegistrationForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.team = self.cleaned_data['team']

        if commit:
            user.save()

        return user


class RegistrationFormTermsOfService(RegistrationForm):
    tos = forms.BooleanField(
        widget=forms.CheckboxInput,
        label=_(u'I have read and agree to the Terms of Service'),
        error_messages={
            'required': validators.TOS_REQUIRED,
        }
    )


class RegistrationFormUniqueEmail(RegistrationForm):
    def clean_email(self):
        if User.objects.filter(email__iexact=self.cleaned_data['email']):
            raise forms.ValidationError(validators.DUPLICATE_EMAIL)
        return self.cleaned_data['email']


class RegistrationFormNoFreeEmail(RegistrationForm):
    bad_domains = ['aim.com', 'aol.com', 'email.com', 'gmail.com',
                   'googlemail.com', 'hotmail.com', 'hushmail.com',
                   'msn.com', 'mail.ru', 'mailinator.com', 'live.com',
                   'yahoo.com']

    def clean_email(self):
        email_domain = self.cleaned_data['email'].split('@')[1]
        if email_domain in self.bad_domains:
            raise forms.ValidationError(validators.FREE_EMAIL)
        return self.cleaned_data['email']
