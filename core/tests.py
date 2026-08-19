from django.contrib.auth import get_user_model
from django.test import override_settings
from django.test import TestCase
from django.urls import reverse

from events.models import CasualGame, CasualGameSession, Tournament, Team, MatchScore


class ResultsPageTests(TestCase):
    def setUp(self):
        self.game = CasualGame.objects.create(name='VR Gaming')
        self.session = CasualGameSession.objects.create(
            game=self.game, player_name='Agent Vega', status='Playing'
        )

    def test_results_page_renders_public_standings(self):
        tournament = Tournament.objects.create(name='BGMI', game_type='Battle Royale')
        team = Team.objects.create(tournament=tournament, team_name='Alpha Squad')
        MatchScore.objects.create(team=team, match_number=1, placement_points=10, kill_points=4)

        response = self.client.get(reverse('core:results'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Alpha Squad')
        self.assertContains(response, '14 PTS')
        self.assertNotContains(response, 'name="action" value="toggle_status"')

    def test_only_staff_can_toggle_a_session(self):
        url = reverse('core:results')
        response = self.client.post(url, {'action': 'toggle_status', 'session_id': self.session.pk})
        self.assertRedirects(response, url)
        self.session.refresh_from_db()
        self.assertEqual(self.session.status, 'Playing')

        staff = get_user_model().objects.create_user('operator', password='secret', is_staff=True)
        self.client.force_login(staff)
        response = self.client.post(url, {'action': 'toggle_status', 'session_id': self.session.pk})
        self.assertRedirects(response, url)
        self.session.refresh_from_db()
        self.assertEqual(self.session.status, 'Completed')

    def test_invalid_session_is_handled_without_a_server_error(self):
        staff = get_user_model().objects.create_user('operator', password='secret', is_staff=True)
        self.client.force_login(staff)

        response = self.client.post(
            reverse('core:results'), {'action': 'toggle_status', 'session_id': 'not-a-number'}
        )

        self.assertRedirects(response, reverse('core:results'))

    @override_settings(RESULTS_DATA_ENABLED=False)
    def test_results_page_stays_available_when_hosted_database_is_not_configured(self):
        response = self.client.get(reverse('core:results'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Results are being prepared for publication.')
