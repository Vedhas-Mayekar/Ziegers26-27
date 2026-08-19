from django.contrib import admin
from django.urls import path
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
import math
from .models import CasualGame, PreRegisteredPlayer, CasualGameSession, Tournament, Team, Match, MatchScore

# --- CASUAL / WALK-IN ADMINS ---

class PreRegisteredPlayerInline(admin.TabularInline):
    model = PreRegisteredPlayer
    extra = 1

@admin.register(CasualGame)
class CasualGameAdmin(admin.ModelAdmin):
    list_display = ('name',)
    inlines = [PreRegisteredPlayerInline]

@admin.register(CasualGameSession)
class CasualGameSessionAdmin(admin.ModelAdmin):
    list_display = ('player_name', 'game', 'check_in_time', 'status', 'is_walkin')
    list_filter = ('game', 'status', 'is_walkin')


# --- TOURNAMENT ADMINS ---

class MatchScoreInline(admin.TabularInline):
    model = MatchScore
    extra = 1

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('team_name', 'tournament', 'leader_ign')
    inlines = [MatchScoreInline]

@admin.register(Tournament)
class TournamentAdmin(admin.ModelAdmin):
    list_display = ('name', 'game_type', 'max_players_per_team')

@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ('tournament', 'round_number', 'match_number', 'bracket_side', 'team1', 'team2', 'winner')
    list_filter = ('tournament', 'round_number', 'bracket_side')

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('draw-bracket/', self.admin_site.admin_view(self.draw_bracket_view), name='events_match_draw_bracket'),
        ]
        return custom_urls + urls

    def draw_bracket_view(self, request):
        tournaments = Tournament.objects.filter(game_type='1v1')
        selected_tournament_id = request.GET.get('tournament_id') or request.POST.get('tournament_id')
        
        tournament = None
        teams = []
        matches_by_round = {}

        if selected_tournament_id:
            tournament = get_object_or_404(Tournament, pk=selected_tournament_id)
            teams = list(Team.objects.filter(tournament=tournament))

            if request.method == "POST" and "reset_bracket" in request.POST:
                Match.objects.filter(tournament=tournament).delete()
                target_slots = int(request.POST.get("bracket_size", 32))
                rounds = int(math.log2(target_slots))
                
                m_num = 1
                curr_matches = target_slots // 2
                for r in range(1, rounds + 1):
                    for m in range(curr_matches):
                        side = 'Left'
                        if r == rounds:
                            side = 'Final'
                        elif m >= (curr_matches // 2):
                            side = 'Right'

                        Match.objects.create(
                            tournament=tournament,
                            round_number=r,
                            match_number=m_num,
                            bracket_side=side
                        )
                        m_num += 1
                    curr_matches //= 2
                
                messages.success(request, f"Generated blank bracket with {target_slots} slots!")
                return redirect(request.path + f"?tournament_id={tournament.id}")

            if not Match.objects.filter(tournament=tournament).exists():
                num_teams = len(teams)
                target_slots = 32 if num_teams <= 32 and num_teams > 0 else (2 ** math.ceil(math.log2(num_teams)) if num_teams > 0 else 32)
                rounds = int(math.log2(target_slots))
                
                m_num = 1
                curr_matches = target_slots // 2
                for r in range(1, rounds + 1):
                    for m in range(curr_matches):
                        side = 'Left'
                        if r == rounds:
                            side = 'Final'
                        elif m >= (curr_matches // 2):
                            side = 'Right'

                        Match.objects.create(
                            tournament=tournament,
                            round_number=r,
                            match_number=m_num,
                            bracket_side=side
                        )
                        m_num += 1
                    curr_matches //= 2

            if request.method == "POST" and "save_bracket" in request.POST:
                for key, val in request.POST.items():
                    if key.startswith("match_"):
                        parts = key.split("_")
                        match_id = parts[1]
                        field_type = parts[2]
                        
                        match_obj = Match.objects.filter(id=match_id).first()
                        if match_obj:
                            team_obj = Team.objects.filter(id=val).first() if val and val != "BYE" else None
                            if field_type == "team1":
                                match_obj.team1 = team_obj
                            elif field_type == "team2":
                                match_obj.team2 = team_obj
                            elif field_type == "winner":
                                match_obj.winner = team_obj
                            
                            if val == "BYE":
                                match_obj.is_bye = True
                            
                            match_obj.save()

                messages.success(request, "Bracket structure updated successfully!")
                return redirect(request.path + f"?tournament_id={tournament.id}")

            all_matches = Match.objects.filter(tournament=tournament).order_by('round_number', 'match_number')
            for m in all_matches:
                matches_by_round.setdefault(m.round_number, []).append(m)

        return render(request, 'admin/draw_bracket.html', {
            'tournaments': tournaments,
            'selected_tournament': tournament,
            'teams': teams,
            'matches_by_round': matches_by_round,
            'opts': self.model._meta
        })