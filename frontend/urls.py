from django.urls import path
from .views import *

urlpatterns = [
    path('', login_page),
    path('dashboard/', dashboard_page),
    path('projects/', projects_page),
    path('tasks/', tasks_page),
    path('upgrade/', upgrade_page),
    path("team/", team_page),
]