# TeamFlow

![Tests](https://github.com/ash00win/TeamFlow/actions/workflows/tests.yml/badge.svg)

TeamFlow is a multi-tenant project and task management SaaS built with Django and Django REST Framework. Each company gets an isolated workspace with role-based access control, a Free/Pro plan tier, an audit trail, and background email jobs powered by Celery.

**Live demo:** https://teamflow-web-10tl.onrender.com — [API docs](https://teamflow-web-10tl.onrender.com/api/docs/) (Swagger UI)

Runs on Render's free tier, so the instance spins down after ~15 minutes of inactivity — the first request after that can take 30-50 seconds to wake it back up. The Celery worker/beat jobs (scheduled reminder emails) aren't deployed here since Render's free plan doesn't support background worker processes; everything else — auth, multi-tenant isolation, RBAC, plan limits, audit log — runs live against a real Postgres database. See [Setup (Docker)](#setup-docker) below to run the full stack including Celery locally.

## Features

- JWT authentication (SimpleJWT), with rate limiting on login/register to slow down brute-force/spam attempts
- Custom user model with company-scoped roles (Owner / Manager / Member)
- Multi-tenant data isolation — every query is scoped to `request.user.company`
- Project and task management via a DRF `ModelViewSet` API
- Role-based permissions (e.g. only Owners can delete projects or add users)
- Free plan is capped at 3 projects per company; upgrading to Pro lifts the cap
- Audit log of key actions (project created/deleted, task created, user added, plan changed), visible to company Owners
- Auto-generated OpenAPI schema + Swagger/Redoc docs
- Server-rendered dashboard, projects, tasks, team, and upgrade pages
- Scheduled background jobs via Celery Beat: overdue task reminders, weekly project summaries, subscription expiry alerts

## Tech Stack

- **Backend:** Python, Django, Django REST Framework
- **Auth:** JWT (djangorestframework-simplejwt)
- **Background jobs:** Celery + Redis (broker), django-celery-beat (scheduler)
- **Database:** SQLite for zero-config local dev; Postgres in Docker/production (switches automatically via `DATABASE_URL`)
- **API docs:** drf-spectacular (OpenAPI schema, Swagger UI, Redoc)
- **Frontend:** Django templates (no separate SPA yet)
- **Config:** environment variables via django-environ

## Project layout

- `accounts/` — the core app: models (`Company`, `User`, `Membership`, `Project`, `Task`, `AuditLog`), DRF views/serializers/permissions, and Celery tasks
- `frontend/` — server-rendered pages (login, signup, dashboard, projects, tasks, team, upgrade)
- `config/` — Django settings, URL routing, Celery app config

## Setup (local, no Docker)

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

This mode uses SQLite and needs no other services running. To also run the background jobs, you need Redis running locally plus a Celery worker + beat process:

```bash
celery -A config worker -l info
celery -A config beat -l info
```

## Setup (Docker)

```bash
docker compose up --build
```

This starts the Django app, Postgres, Redis, and both the Celery worker and beat scheduler together, and runs migrations automatically. The app is then available at `http://localhost:8000`.

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
| `/api/audit-logs/` | GET | Owner views the company's audit trail |

Full interactive docs: `/api/docs/` (Swagger UI) and `/api/redoc/` (Redoc). Raw schema at `/api/schema/`.

## Tests

```bash
python manage.py test
```
