# TeamFlow

TeamFlow is a multi-tenant project and task management SaaS built with Django and Django REST Framework. Each company gets an isolated workspace with role-based access control, a Free/Pro plan tier, and background email jobs powered by Celery.

## Features

- JWT authentication (SimpleJWT)
- Custom user model with company-scoped roles (Owner / Manager / Member)
- Multi-tenant data isolation — every query is scoped to `request.user.company`
- Project and task management via a DRF `ModelViewSet` API
- Role-based permissions (e.g. only Owners can delete projects or add users)
- Free plan is capped at 3 projects per company; upgrading to Pro lifts the cap
- Server-rendered dashboard, projects, tasks, team, and upgrade pages
- Scheduled background jobs via Celery Beat: overdue task reminders, weekly project summaries, subscription expiry alerts

## Tech Stack

- **Backend:** Python, Django, Django REST Framework
- **Auth:** JWT (djangorestframework-simplejwt)
- **Background jobs:** Celery + Redis (broker), django-celery-beat (scheduler)
- **Database:** SQLite in development; swap `DATABASES` in `config/settings.py` for Postgres/MySQL in production
- **Frontend:** Django templates (no separate SPA yet)
- **Config:** environment variables via django-environ

## Project layout

- `accounts/` — the core app: models (`Company`, `User`, `Membership`, `Project`, `Task`), DRF views/serializers/permissions, and Celery tasks
- `frontend/` — server-rendered pages (login, signup, dashboard, projects, tasks, team, upgrade)
- `config/` — Django settings, URL routing, Celery app config

## Setup

```bash
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

pip install -r requirements.txt
cp .env.example .env         # then fill in your own SECRET_KEY

python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

To run the background jobs, you also need Redis running locally and a Celery worker + beat process:

```bash
celery -A config worker -l info
celery -A config beat -l info
```

## API overview

| Endpoint | Method | Description |
|---|---|---|
| `/api/register/` | POST | Register a new company + owner account |
| `/api/login/` | POST | Obtain JWT access/refresh tokens |
| `/api/token/refresh/` | POST | Refresh an access token |
| `/api/protected/` | GET | Example authenticated endpoint |
| `/api/projects/` | GET/POST | List or create projects (company-scoped) |
| `/api/tasks/` | GET/POST | List or create tasks (company-scoped) |
| `/api/add-user/` | POST | Owner adds a Manager/Member to their company |
| `/api/upgrade-plan/` | POST | Owner upgrades/downgrades the company plan |

## Tests

```bash
python manage.py test
```
