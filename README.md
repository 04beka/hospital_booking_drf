# Hospital Booking (DRF) — Exam Project

## Features
- Custom User (email login) with required fields + validations
- Email verification (6-digit code, 20 min expiry, 60s resend cooldown)
- JWT auth (SimpleJWT) — login blocked until email is verified
- Recovery question (hashed answer) + password reset link via email
- Doctors (data-only) + Availability Slots (60 min)
- Appointments: book/cancel/reschedule (>=2 hours rule), 1 patient per slot
- Dockerized (Django + PostgreSQL)
- Seed demo data command

## Quick start (Docker)
1. Copy `.env.example` to `.env` and fill values.
2. Run:
   ```bash
   docker compose up --build
   ```
3. Apply migrations + create admin:
   ```bash
   docker compose exec web python manage.py migrate
   docker compose exec web python manage.py createsuperuser
   docker compose exec web python manage.py seed_demo
   ```

API is served at: `http://localhost:8000/`

## Local run (without Docker)
```bash
python -m venv .venv
source .venv/bin/activate  # (Windows: .venv\Scripts\activate)
pip install -r requirements.txt
cp .env .env
python manage.py migrate
python manage.py createsuperuser
python manage.py seed_demo
python manage.py runserver
```

## Core endpoints
- POST `/api/auth/register/`
- POST `/api/auth/verify-email/`
- POST `/api/auth/resend-code/`
- POST `/api/auth/token/` (JWT)  (blocked if email not verified)
- POST `/api/auth/token/refresh/`
- POST `/api/auth/recovery/verify/`
- POST `/api/auth/password-reset/request/`
- POST `/api/auth/password-reset/confirm/`

- GET `/api/doctors/`
- GET `/api/doctors/{id}/slots/`

- POST `/api/appointments/`
- GET  `/api/appointments/my/`
- POST `/api/appointments/{id}/cancel/`
- POST `/api/appointments/{id}/reschedule/`

Admin:
- `/api/admin/users/`
- `/api/admin/doctors/`
- `/api/admin/slots/`
- `/api/admin/appointments/`
