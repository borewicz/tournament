from django.db import models
from custom_user.models import AbstractEmailUser
from django.conf import settings
from django.dispatch import receiver
from registration.signals import user_registered


class Sponsor(models.Model):
    name = models.CharField(max_length=50)
    picture = models.ImageField(upload_to='upload/', default='default.jpg')

    def __str__(self):
        return self.name


class User(AbstractEmailUser):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    team = models.CharField(max_length=50, unique=True, null=False)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'team']

    def __str__(self):
        return "%s %s (%s)" % (self.first_name, self.last_name, self.email)


class Tournament(models.Model):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=100)
    deadline = models.DateTimeField()
    date = models.DateTimeField()
    longitude = models.FloatField()
    latitude = models.FloatField()
    sponsors = models.ManyToManyField(Sponsor, blank=True)
    limit = models.IntegerField()
    seeded_players = models.IntegerField()
    organizer = models.ForeignKey(settings.AUTH_USER_MODEL)

    def __str__(self):
        return "%s (%s)" % (self.name, self.description)


class Enrollment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    tournament = models.ForeignKey(Tournament)
    ranking = models.IntegerField(unique=True)
    license_id = models.IntegerField(unique=True)

    def __str__(self):
        return "%s joined %s" % (self.user.name, self.tournament.name)


@receiver(user_registered)
def user_registered_handler(sender, user, request, **kwargs):
    user.first_name = request.POST.get('first_name')
    user.last_name = request.POST.get('last_name')
    user.save()
