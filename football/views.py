from django.shortcuts import render_to_response, redirect, render
from django.core.urlresolvers import reverse_lazy
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Tournament, Enrollment
from .forms import EnrollForm
from django.contrib.auth.decorators import login_required


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
    count = tournament.limit - Enrollment.objects.filter(tournament=tournament).count()
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
