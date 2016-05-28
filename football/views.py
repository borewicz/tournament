from django.shortcuts import render_to_response, redirect, render
from django.core.urlresolvers import reverse_lazy
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Tournament, Enrollment, Sponsor
from .forms import EnrollForm, TournamentForm
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse


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
    return render(request, "detail.html",
                  {"tournament": tournament,
                   "count": count,
                   "enrolled": enrolled})


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
