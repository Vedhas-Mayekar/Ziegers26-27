"""URL configuration for the core application."""
from django.urls import path
from django.views.generic import RedirectView

from . import views

app_name = 'core'

urlpatterns = [
    # Backwards-compatible route for old login redirects/bookmarks. Keep the
    # `next` query string so the admin login returns users to the desk page.
    path(
        'accounts/login/',
        RedirectView.as_view(url='/admin/login/', query_string=True),
        name='login_redirect',
    ),
    # Chrome DevTools mobile-emulation probe (avoids debugger pause on 404)
    path(
        '.well-known/appspecific/com.chrome.devtools.json',
        views.chrome_devtools_probe,
        name='chrome_devtools_probe'
    ),
    # Landing page
    path('', views.landing_page, name='landing'),
    # Results page
    path('results/', views.results_page, name='results'),
    # Command Crew page
    path('command-crew/', views.command_crew_page, name='command_crew'),
]
