from django.db import models
from custom_user.models import AbstractEmailUser
from django.conf import settings
from django.dispatch import receiver
from registration.signals import user_registered
from django.db.models import signals


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


class Round(models.Model):
    tournament = models.ForeignKey(Tournament)
    name = models.IntegerField(blank=False)
    seeded = models.BooleanField()


class Pair(models.Model):
    round = models.ForeignKey(Round, related_name="round")
    player_1 = models.ForeignKey(User, related_name="player_1")
    player_2 = models.ForeignKey(User, related_name="player_2")
    winner = models.ForeignKey(User, null=True, related_name="winner")
    result_player_1 = models.IntegerField(blank=True)
    result_player_2 = models.IntegerField(blank=True)

    def __str__(self):
        return "round %d: %s %d - %s %d" % (
            self.round_id, self.player_1, self.result_player_1, self.player_2, self.result_player_2)

    def set_result(self, result_1, result_2):
        if self.result_player_1.blank and self.result_player_2.blank:
            self.result_player_1 = result_1
            self.result_player_2 = result_2
        else:
            if self.result_player_2 == result_1 and self.result_player_2 == result_2:
                self.winner = self.player_1 if result_1 > result_2 else self.player_2
            else:
                self.result_player_1 = self.result_player_2 = None
        self.save()


def generate_pairs(sender, instance, created, **kwargs):
    unfinished = sender.objects.filter(winner__isnull=True, round=instance.round)
    if not unfinished.count:
        if instance.round.seeded:
            pass
        else:
            teams = [i.winner for i in sender.objects.filter(round=instance.round)]
            # tutej new round
            # for team in teams:
            #     pair = Pair()

signals.post_save.connect(generate_pairs, sender=Pair)
