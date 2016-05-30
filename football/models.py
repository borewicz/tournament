from django.db import models
from custom_user.models import AbstractEmailUser
from django.conf import settings
from django.dispatch import receiver
from registration.signals import user_registered
from django.db.models import signals, Max
import random
from model_utils import FieldTracker


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
        return "%s %s" % (self.first_name, self.last_name)


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
    in_progress = models.BooleanField(default=False)

    def __str__(self):
        return "%s (%s)" % (self.name, self.description)


class Enrollment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    tournament = models.ForeignKey(Tournament)
    ranking = models.IntegerField(unique=True)
    license_id = models.IntegerField(unique=True)

    def __str__(self):
        return "%s joined %s" % (self.user, self.tournament.name)


@receiver(user_registered)
def user_registered_handler(sender, user, request, **kwargs):
    user.first_name = request.POST.get('first_name')
    user.last_name = request.POST.get('last_name')
    user.save()


class Round(models.Model):
    tournament = models.ForeignKey(Tournament)
    name = models.IntegerField(blank=False)
    seeded = models.BooleanField()


class Match(models.Model):
    round = models.ForeignKey(Round, related_name="round")
    player_1 = models.ForeignKey(User, related_name="player_1")
    player_2 = models.ForeignKey(User, related_name="player_2")
    winner = models.ForeignKey(User, null=True, blank=True, related_name="winner")
    score = models.CharField(max_length=5, null=False, default='-')
    tracker = FieldTracker()
    last_filled = models.ForeignKey(User, related_name="last_filled", null=True, blank=True)

    def __str__(self):
        return "round %d: %s - %s" % (
            self.round.name, self.player_1.team, self.player_2.team)

    @classmethod
    def update_bracket(cls, teams, tournament, seeded=False):
        new_round = Round()
        new_round.tournament = tournament
        new_round.name = Round.objects.all().aggregate(Max('name'))['name__max'] + 1 if Round.objects.count() else 1
        new_round.seeded = seeded
        new_round.save()
        if seeded:
            seeded_teams = teams[:tournament.seeded_players]
            teams = teams[tournament.seeded_players:]
        else:
            seeded_teams = []
        for team in seeded_teams:
            opponent = random.choice(teams)
            Match.objects.create(round=new_round,
                                 player_1=team,
                                 player_2=opponent)
            teams.remove(opponent)
        while len(teams) != 0:
            team = random.choice(teams)
            while True:
                opponent = random.choice(teams)
                if team != opponent:
                    break
            Match.objects.create(round=new_round,
                                 player_1=team,
                                 player_2=opponent)
            teams.remove(opponent)
            teams.remove(team)


def generate_tournament_bracket(sender, instance, created, **kwargs):
    if created or instance.tracker.previous('score') == '-':
        return
    if instance.tracker.has_changed('score'):
        sender.objects.filter(pk=instance.pk).update(winner=None,
                                                     score='-',
                                                     last_filled=None)
        return
    score = instance.score.split(':')
    winner = instance.player_1 if int(score[0]) > int(score[1]) else instance.player_2
    sender.objects.filter(pk=instance.pk).update(winner=winner)
    unfinished = sender.objects.filter(winner__isnull=True, round=instance.round)
    if unfinished.count() == 0:
        teams = [e.winner for e in Match.objects.filter(round=instance.round)]
        if len(teams) == 1:
            return
        Match.update_bracket(teams, instance.round.tournament, seeded=instance.round.seeded)

signals.post_save.connect(generate_tournament_bracket, sender=Match)
