from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from django.core.mail import send_mail

from .models import Task, Project, Company

@shared_task
def send_overdue_task_reminders():

    today = timezone.now().date()

    overdue_tasks = Task.objects.exclude(status="DONE").filter(
        due_date__lt=today,
        due_date__isnull=False,
        assigned_to__isnull=False,
    )

    sent = 0

    for task in overdue_tasks:

        user = task.assigned_to

        if not user.email:
            continue

        send_mail(
            subject="Task Overdue Reminder",
            message=f"The task '{task.title}' is overdue.",
            from_email="noreply@teamflow.com",
            recipient_list=[user.email],
            fail_silently=True,
        )
        sent += 1

    return f"{sent} reminders sent"


@shared_task
def weekly_project_summary():

    projects = Project.objects.select_related("created_by").all()
    sent = 0

    for project in projects:

        owner = project.created_by

        if not owner or not owner.email:
            continue

        total_tasks = project.tasks.count()
        completed_tasks = project.tasks.filter(status="DONE").count()

        message = f"""
Weekly Project Summary

Project: {project.name}

Total Tasks: {total_tasks}
Completed Tasks: {completed_tasks}
"""

        send_mail(
            subject="Weekly Project Summary",
            message=message,
            from_email="noreply@teamflow.com",
            recipient_list=[owner.email],
            fail_silently=True,
        )
        sent += 1

    return f"{sent} summaries sent"

@shared_task
def subscription_expiry_alert():

    today = timezone.now().date()

    companies = Company.objects.filter(
        plan="PRO",
        expiry_date__isnull=False,
        expiry_date__lte=today + timedelta(days=3),
    )

    sent = 0

    for company in companies:

        owner = company.users.filter(role="OWNER").first()

        if not owner or not owner.email:
            continue

        send_mail(
            subject="Subscription Expiry Warning",
            message=f"Your TeamFlow PRO plan for '{company.name}' expires on {company.expiry_date}.",
            from_email="noreply@teamflow.com",
            recipient_list=[owner.email],
            fail_silently=True,
        )
        sent += 1

    return f"{sent} subscription alerts sent"
