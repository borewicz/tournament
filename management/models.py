from django.db import models
from custom_user.models import AbstractEmailUser


class Sponsor(models.Model):
    name = models.TextField()
    picture = models.ImageField(upload_to='upload/', default='default.jpg')

    def __str__(self):
        return self.name


class User(AbstractEmailUser):
    name = models.TextField(max_length=50)
    surname = models.TextField(max_length=50)
    USERNAME_FIELD = 'email'

    def __str__(self):
        return "%s %s (%s)" % (self.name, self.surname, self.email)


class Tournament(models.Model):
    name = models.TextField(max_length=50)
    discipline = models.TextField(max_length=50)
    description = models.TextField(max_length=100)
    deadline = models.DateTimeField()
    date = models.DateTimeField()
    longitude = models.FloatField()
    latitude = models.FloatField()
    sponsors = models.ManyToManyField(Sponsor, blank=True)
    limit = models.IntegerField()
    seeded_players = models.IntegerField()
    organizer = models.ForeignKey(User)

    def __str__(self):
        return "%s (%s)" % (self.name, self.discipline)


class Enrollment(models.Model):
    user = models.ForeignKey(User)
    tournament = models.ForeignKey(Tournament)
    ranking = models.IntegerField(unique=True)
    license_id = models.IntegerField(unique=True)

    def __str__(self):
        return "%s joined %s" % (self.user.name, self.tournament.name)
