from django.shortcuts import render

def login_page(request):
    return render(request, "login.html")

def dashboard_page(request):
    return render(request, "dashboard.html")

def projects_page(request):
    return render(request, "projects.html")

def tasks_page(request):
    return render(request, "tasks.html")

def upgrade_page(request):
    return render(request, "upgrade.html")

def team_page(request):
    return render(request,"team.html")