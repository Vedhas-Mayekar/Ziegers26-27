"""Views for the ZIEGERS DeCipher Gaming operations desk.

Every page here extends the shared noir / DeCipher theme (``core/base.html``)
so the gaming division keeps a single, consistent visual identity with the
rest of the bureau.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test

from .models import CasualGame, PreRegisteredPlayer, CasualGameSession, Tournament, Team, Match


def index(request):
    """Tournament index — active case files rendered as evidence-board cards."""
    tournaments = Tournament.objects.all()
    casual_count = CasualGameSession.objects.count()
    return render(request, 'events/index.html', {
        'tournaments': tournaments,
        'casual_count': casual_count,
    })


def is_staff_user(user):
    return user.is_staff


@login_required
@user_passes_test(is_staff_user, login_url='/admin/login/')
def casual_log(request):
    """Operational desk: manage pre-registered + walk-in casual sessions.

    Staff toggle session status (Playing <-> Completed) and dispatch
    pre-registered agents or on-the-spot walk-ins directly from this log.
    """
    games = CasualGame.objects.all()

    if request.method == 'POST':
        action = request.POST.get('action')

        # 1. Pre-Registered Player Check-In
        if action == 'checkin_preregistered':
            player_id = request.POST.get('player_id')
            player = get_object_or_404(PreRegisteredPlayer, pk=player_id)

            CasualGameSession.objects.create(
                game=player.game,
                player_name=player.player_name,
                status='Playing',
                is_walkin=False
            )
            player.is_checked_in = True
            player.save()

        # 2. Add On-the-spot Walk-in Player
        elif action == 'add_walkin':
            name = request.POST.get('player_name')
            game_id = request.POST.get('game_id')
            game = get_object_or_404(CasualGame, pk=game_id) if game_id else None

            if name:
                CasualGameSession.objects.create(
                    game=game,
                    player_name=name,
                    status='Playing',
                    is_walkin=True
                )

        # 3. Toggle Status (Playing <-> Completed)
        elif action == 'toggle_status':
            session_id = request.POST.get('session_id')
            session = get_object_or_404(CasualGameSession, pk=session_id)
            session.status = 'Completed' if session.status == 'Playing' else 'Playing'
            session.save()

        return redirect('events:casual_log')

    sessions = CasualGameSession.objects.all().order_by('-check_in_time')
    return render(request, 'events/casual_log.html', {
        'games': games,
        'sessions': sessions
    })


def tournament_detail(request, tournament_id):
    """Render a single tournament's bracket (1v1) or points table (Battle Royale)."""
    tournament = get_object_or_404(Tournament, pk=tournament_id)
    teams = Team.objects.filter(tournament=tournament)

    matches_by_round = {}
    if tournament.game_type == '1v1':
        matches = Match.objects.filter(tournament=tournament).order_by('round_number', 'match_number')
        for match in matches:
            matches_by_round.setdefault(match.round_number, []).append(match)

    return render(request, 'events/tournament.html', {
        'tournament': tournament,
        'teams': teams,
        'matches_by_round': matches_by_round,
    })
