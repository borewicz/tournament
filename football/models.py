from django.db import models
from custom_user.models import AbstractEmailUser
from django.conf import settings
from django.dispatch import receiver
from registration.signals import user_registered
from django.db.models import signals
import random


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


class Pair(models.Model):
    round = models.ForeignKey(Round, related_name="round")
    player_1 = models.ForeignKey(User, related_name="player_1")
    player_2 = models.ForeignKey(User, related_name="player_2")
    winner = models.ForeignKey(User, null=True, blank=True, related_name="winner")
    result_player_1 = models.IntegerField(null=True)
    result_player_2 = models.IntegerField(null=True)

    def __str__(self):
        return "round %d: %s - %s" % (
            self.round_id, self.player_1, self.player_2)

    def set_result(self, result_1, result_2):
        if self.result_player_1 is not None and self.result_player_2 is not None:
            self.result_player_1 = result_1
            self.result_player_2 = result_2
        else:
            if self.result_player_2 == result_1 and self.result_player_2 == result_2:
                self.winner = self.player_1 if result_1 > result_2 else self.player_2
            else:
                self.result_player_1 = self.result_player_2 = None
        

def generate_pairs(sender, instance, created, **kwargs):
    # instance.set_result(instance.result_player_1, instance.result_player_2)
    if instance.result_player_1 > instance.result_player_2:
        sender.objects.filter(pk=instance.pk).update(winner=instance.player_1)
    else:
        sender.objects.filter(pk=instance.pk).update(winner=instance.player_2)
    unfinished = sender.objects.filter(winner__isnull=True, round=instance.round)
    print('siki')
    if not unfinished.count:
        if instance.round.seeded:
            print('seeded')
            pass
        else:
            print('not_seeded')
            teams = [i.winner for i in sender.objects.filter(round=instance.round)]
            new_round = Round(commit=False)
            new_round.tournament = instance.round.tournament
            new_round.name = instance.round.name + 1
            new_round.seeded = False
            new_round.save()
            for team in teams:
                pair = Pair(commit=False)
                pair.round = new_round
                pair.player_1 = team
                while True:
                    opponent = random.choice(team)
                    if team != opponent:
                        break
                pair.player_2 = opponent
                pair.save()
                teams.remove(opponent)
                teams.remove(team)


signals.post_save.connect(generate_pairs, sender=Pair)
