"""URL configuration for the ZIEGERS DeCipher Gaming (events) application."""
from django.urls import path

from . import views

app_name = 'events'

urlpatterns = [
    # Tournament index — the gaming operations desk
    path('', views.index, name='index'),
    # Casual / walk-in player desk log (staff only)
    path('walkins/', views.casual_log, name='casual_log'),
    # Single tournament dossier (bracket or points table)
    path('tournament/<int:tournament_id>/', views.tournament_detail, name='tournament_detail'),
]
