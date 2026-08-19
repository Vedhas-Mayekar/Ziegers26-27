from django.db import models
from django.core.exceptions import ValidationError

# --- CASUAL / WALK-IN MODELS ---

class CasualGame(models.Model):
    name = models.CharField(max_length=100, help_text="e.g. VR Gaming, WWE 2K24")
    
    def __str__(self):
        return self.name

class PreRegisteredPlayer(models.Model):
    game = models.ForeignKey(CasualGame, on_delete=models.CASCADE, related_name="pre_registered_players")
    player_name = models.CharField(max_length=100)
    contact = models.CharField(max_length=15, blank=True)
    is_checked_in = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.player_name} ({self.game.name})"

class CasualGameSession(models.Model):
    game = models.ForeignKey(CasualGame, on_delete=models.SET_NULL, null=True, blank=True, related_name="sessions")
    player_name = models.CharField(max_length=100)
    check_in_time = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20, 
        choices=[('Playing', 'Playing'), ('Completed', 'Completed')], 
        default='Playing'
    )
    is_walkin = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.player_name} - {self.game.name if self.game else 'General'}"

class Tournament(models.Model):
    name = models.CharField(max_length=100)
    game_type = models.CharField(
        max_length=20, 
        choices=[('1v1', '1v1 Knockout'), ('Battle Royale', 'Battle Royale Points')]
    )
    max_players_per_team = models.PositiveIntegerField(default=4, help_text="Maximum allowed players per team")

    def __str__(self):
        return f"{self.name} ({self.get_game_type_display()})"

class Team(models.Model):
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name="teams")
    team_name = models.CharField(max_length=100)
    leader_name = models.CharField(max_length=100, default="")
    leader_ign = models.CharField(max_length=100, default="")
    leader_contact = models.CharField(max_length=15, default="", blank=True)
    
    # NEW: Notes / Important stuff field
    notes = models.TextField(blank=True, null=True, help_text="Notes or important stuff for this team (e.g. substitutes, payment info, warnings)")

    def __str__(self):
        return f"{self.team_name} ({self.tournament.name})"

    @property
    def total_br_points(self):
        return sum(score.total_points for score in self.scores.all())

    @property
    def wins_count(self):
        return Match.objects.filter(winner=self).count()

    @property
    def losses_count(self):
        return Match.objects.filter(tournament=self.tournament).filter(
            models.Q(team1=self) | models.Q(team2=self)
        ).exclude(winner=self).exclude(winner__isnull=True).count()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.leader_ign:
            player, created = Player.objects.get_or_create(
                team=self,
                in_game_name=self.leader_ign,
                defaults={'contact': self.leader_contact}
            )
            if not created and player.contact != self.leader_contact:
                player.contact = self.leader_contact
                player.save()

class Player(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="players")
    in_game_name = models.CharField(max_length=100)
    contact = models.CharField(max_length=15, blank=True)

    def clean(self):
        if not self.pk and self.team_id and hasattr(self.team, 'tournament') and self.team.tournament:
            max_allowed = self.team.tournament.max_players_per_team
            current_count = self.team.players.count()
            if current_count >= max_allowed:
                raise ValidationError(f"Cannot add player! Max limit of {max_allowed} players reached.")

    def __str__(self):
        return f"{self.in_game_name} ({self.team.team_name})"

class MatchScore(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="scores")
    match_number = models.PositiveIntegerField(default=1, help_text="e.g. 1 for Match 1, 2 for Match 2")
    placement_points = models.PositiveIntegerField(default=0)
    kill_points = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('team', 'match_number')
        ordering = ['match_number']

    @property
    def total_points(self):
        return self.placement_points + self.kill_points

    def __str__(self):
        return f"{self.team.team_name} - Match #{self.match_number}: {self.total_points} pts"

class Match(models.Model):
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name="matches")
    round_number = models.IntegerField(default=1)
    match_number = models.IntegerField(default=1)
    bracket_side = models.CharField(
        max_length=10, 
        choices=[('Left', 'Left Side'), ('Right', 'Right Side'), ('Final', 'Finals')], 
        default='Left'
    )
    team1 = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, blank=True, related_name="team1_matches")
    team2 = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, blank=True, related_name="team2_matches")
    winner = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, blank=True, related_name="won_matches")
    is_bye = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Brackets for 1v1 Knockout"
        verbose_name_plural = "Brackets for 1v1 Knockouts"
        ordering = ['round_number', 'match_number']

    def __str__(self):
        return f"R{self.round_number} M{self.match_number}: {self.team1 or 'BYE/TBD'} vs {self.team2 or 'BYE/TBD'}"