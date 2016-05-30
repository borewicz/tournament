from django.shortcuts import render_to_response, redirect, render
from django.core.urlresolvers import reverse_lazy
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Tournament, Enrollment, Sponsor, User, Match, Round
from .forms import EnrollForm, TournamentForm, MatchForm
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
import random


# Create your views here.

def index(request):
    paginator = Paginator(Tournament.objects.all(), 10)
    page = request.GET.get('page')
    try:
        tournaments = paginator.page(page)
    except PageNotAnInteger:
        tournaments = paginator.page(1)
    except EmptyPage:
        tournaments = paginator.page(paginator.num_pages)
    return render(request, 'index.html', {'tournaments': tournaments})


def detail(request, tournament_id):
    tournament = Tournament.objects.get(id=tournament_id)
    count = Enrollment.objects.filter(tournament=tournament).count()
    enrolled = Enrollment.objects.filter(tournament__pk=tournament_id, user__id=request.user.id).count()

    if count == tournament.limit and not tournament.in_progress:
        teams = [e.user for e in Enrollment.objects.filter(tournament=tournament).order_by('-ranking')]
        Match.update_bracket(teams, tournament, seeded=True)
        Tournament.objects.filter(pk=tournament.pk).update(in_progress=True)

    return render(request, "detail.html",
                  {"tournament": tournament,
                   "count": count,
                   "enrolled": enrolled,
                   "enrollments": Enrollment.objects.filter(tournament=tournament),
                   "matches": Match.objects.filter(round__tournament=tournament).order_by('round__name')})


@login_required(login_url=reverse_lazy('auth_login'))
def join(request, tournament_id):
    if request.method == "POST":
        form = EnrollForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.tournament = Tournament.objects.get(pk=tournament_id)
            post.save()
            return redirect('football:detail', tournament_id=tournament_id)
    else:
        form = EnrollForm()
    return render(request, 'enroll.html', {'form': form,
                                           'tournament_id': tournament_id})


@login_required(login_url=reverse_lazy('auth_login'))
def create(request):
    if request.method == "POST":
        form = TournamentForm(request.POST)
        if form.is_valid():
            tournament = form.save(commit=False)
            tournament.organizer = request.user
            tournament.save()
            form.save_m2m()
            return redirect('football:index')
    else:
        form = TournamentForm()
    return render(request, 'create.html', {'form': form,
                                           'label': 'Create tournament'})


@login_required(login_url=reverse_lazy('auth_login'))
def edit(request, tournament_id):
    tournament = Tournament.objects.filter(id=tournament_id)
    if not tournament:
        return HttpResponse("Tournament not exist!")
    if tournament[0].organizer != request.user:
        return HttpResponse("It's not your tournament!")
    if request.method == "POST":
        form = TournamentForm(request.POST, instance=tournament[0])
        if form.is_valid():
            form.save()
            return redirect('football:index')
    else:
        form = TournamentForm(instance=tournament[0])

    return render(request, 'create.html', {'form': form,
                                           'label': 'Edit tournament'})


@login_required(login_url=reverse_lazy('auth_login'))
def update_match(request, match_id):
    match = Match.objects.filter(id=match_id)[0] if Match.objects.filter(id=match_id) else None
    if not match:
        return HttpResponse("Match not exist!")
    if match.player_1 != request.user and match.player_2 != request.user:
        return HttpResponse("It's not your match!")
    # fill = match.fill_1 if match.player_2 == request.user else match.fill_2
    if match.last_filled == request.user:
        return HttpResponse("You already fill!")
    if request.method == "POST":
        form = MatchForm(request.POST, instance=match)
        if form.is_valid():
            match = form.save(commit=False)
            match.last_filled = request.user
            match.save()
            return redirect('football:index')
    else:
        form = MatchForm(instance=match)
    return render(request, 'create.html', {'form': form,
                                           'label': 'Update match'})