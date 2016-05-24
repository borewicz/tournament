from django.db import models

from custom_user.models import AbstractEmailUser


class PortalUser(AbstractEmailUser):
    name = models.TextField(max_length=50)
    surname = models.TextField(max_length=50)
    USERNAME_FIELD = 'email'

    def __str__(self):
        return "%s %s (%s)" % (self.name, self.surname, self.email)
