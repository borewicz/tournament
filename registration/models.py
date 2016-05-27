import datetime
import hashlib
import re
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models, transaction
from django.template.loader import render_to_string
from django.utils.crypto import get_random_string
from django.utils.encoding import python_2_unicode_compatible
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

SHA1_RE = re.compile('^[a-f0-9]{40}$')


class RegistrationManager(models.Manager):
    def activate_user(self, activation_key):
        if SHA1_RE.search(activation_key.lower()):
            try:
                profile = self.get(activation_key=activation_key)
            except self.model.DoesNotExist:
                return False
            if not profile.activation_key_expired():
                user = profile.user
                user.is_active = True
                user.save()
                profile.activation_key = self.model.ACTIVATED
                profile.save()
                return user
        return False

    def expired(self):
        if settings.USE_TZ:
            now = timezone.now()
        else:
            now = datetime.datetime.now()
        return self.filter(
            models.Q(activation_key=self.model.ACTIVATED) |
            models.Q(
                user__date_joined__lt=now - datetime.timedelta(
                    settings.ACCOUNT_ACTIVATION_DAYS
                )
            )
        )

    @transaction.atomic
    def create_inactive_user(self, form, site, send_email=True):
        new_user = form.save(commit=False)
        new_user.is_active = False
        new_user.save()

        registration_profile = self.create_profile(new_user)

        if send_email:
            registration_profile.send_activation_email(site)

        return new_user

    def create_profile(self, user):
        User = get_user_model()
        email = str(getattr(user, User.USERNAME_FIELD))
        hash_input = (get_random_string(5) + email).encode('utf-8')
        activation_key = hashlib.sha1(hash_input).hexdigest()
        return self.create(user=user,
                           activation_key=activation_key)

    @transaction.atomic
    def delete_expired_users(self):
        for profile in self.expired():
            user = profile.user
            profile.delete()
            user.delete()


@python_2_unicode_compatible
class RegistrationProfile(models.Model):
    ACTIVATED = "ALREADY_ACTIVATED"

    user = models.OneToOneField(settings.AUTH_USER_MODEL,
                                verbose_name=_(u'user'))
    activation_key = models.CharField(_(u'activation key'), max_length=40)

    objects = RegistrationManager()

    class Meta:
        verbose_name = _(u'registration profile')
        verbose_name_plural = _(u'registration profiles')

    def __str__(self):
        return "Registration information for %s" % self.user

    def activation_key_expired(self):
        expiration_date = datetime.timedelta(
            days=settings.ACCOUNT_ACTIVATION_DAYS
        )
        return self.activation_key == self.ACTIVATED or \
               (self.user.date_joined + expiration_date <= timezone.now())

    activation_key_expired.boolean = True

    def send_activation_email(self, site):
        """
        Send an activation email to the user associated with this
        ``RegistrationProfile``.

        """
        ctx_dict = {'activation_key': self.activation_key,
                    'expiration_days': settings.ACCOUNT_ACTIVATION_DAYS,
                    'user': self.user,
                    'site': site}
        subject = render_to_string('registration/activation_email_subject.txt',
                                   ctx_dict)
        # Force subject to a single line to avoid header-injection
        # issues.
        subject = ''.join(subject.splitlines())

        message = render_to_string('registration/activation_email.txt',
                                   ctx_dict)

        self.user.email_user(subject, message, settings.DEFAULT_FROM_EMAIL)
