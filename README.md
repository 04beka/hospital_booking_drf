# Hospital Booking (DRF) — Exam Project

## Features
- Custom User (email login)
- Email verification (6-digit code, expiry + resend cooldown)
- JWT authentication (SimpleJWT)
- Login blocked until email is verified AND user is active
- User self-deactivation (soft delete)
- User restore via email verification code
- Recovery question + password reset via email
- Doctors + availability slots
- Appointments (book / cancel / reschedule with ≥2h rule)
- Dockerized (Django + PostgreSQL)
- Demo seed command

---

## API Base URL
http://localhost:8000/api/

---

## ENV CONFIGURATION (IMPORTANT)

### .env file
The `.env` file contains sensitive information (SECRET_KEY, database credentials, email passwords).

For security reasons, **`.env` is NOT included in the repository** and is ignored via `.gitignore`.

### .env.example
The project includes a `.env.example` file which serves as a template.

To run the project:
1. Copy `.env.example`
2. Rename it to `.env`
3. Fill in your own values

Example (Windows PowerShell):
copy .env.example .env

Example (Linux/Mac):
cp .env.example .env

The application will not start without a properly configured `.env` file.

---

## AUTH FLOW (TESTED)

### Register
POST /api/auth/register/

{
  "email": "test@mail.com",
  "password": "Test12345!",
  "first_name": "Test",
  "last_name": "User",
  "recovery_question": "DOG_NAME",
  "recovery_answer": "dog",
  "birth_date": "1993-02-04",
  "gender": "M",
  "personal_id": "12345678901"
}
Note: All fields above are required by RegisterSerializer.

---

### Verify Email
POST /api/auth/verify-email/

{
  "email": "test@mail.com",
  "code": "123456"
}

---

### Resend verification code (if code is lost or expired)
POST /api/auth/resend-code/

{
  "email": "test@mail.com"
}

Notes:
- Works only if the email is NOT verified yet
- Has a cooldown (rate limit) to prevent spam

---

### Login (JWT)
POST /api/auth/login/

{
  "email": "test@mail.com",
  "password": "Test123!"
}

Response:
{
  "access": "...",
  "refresh": "..."
}

Login is blocked if:
- email is not verified
- user is deactivated

---

## USER SELF DELETE (SOFT DELETE)

### Deactivate own account
POST /api/auth/me/delete/

Headers:
Authorization: Bearer <ACCESS_TOKEN>

Response:
{
  "message": "User deactivated"
}

After deactivation:
- Login ❌
- Restore ✅

---

## USER RESTORE (TESTED)

### Request restore code
POST /api/auth/restore/request/

{
  "email": "test@mail.com"
}

Restore code is sent to email.

---

### Confirm restore
POST /api/auth/restore/confirm/

{
  "email": "test@mail.com",
  "code": "654321"
}

Response:
{
  "message": "User restored"
}

---

### Login again
POST /api/auth/login/

Login works again after restore.

---

## PASSWORD RECOVERY

### Verify recovery question
POST /api/auth/recovery/verify/

### Password reset request
POST /api/auth/password-reset/request/

### Password reset confirm
POST /api/auth/password-reset/confirm/

---

## DOCTORS & SLOTS

GET /api/doctors/
GET /api/doctors/{id}/slots/

---

## APPOINTMENTS

POST /api/appointments/
GET  /api/appointments/my/
POST /api/appointments/{id}/cancel/
POST /api/appointments/{id}/reschedule/

Rules:
- One appointment per slot
- Reschedule allowed only 2+ hours before appointment

---

## LOCAL RUN (WITHOUT DOCKER)

python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
copy .env.example .env
python manage.py migrate
python manage.py runserver

---

## DOCKER

docker compose up --build
docker compose exec web python manage.py migrate
docker compose exec web python manage.py seed_demo

---

## SUMMARY
- Endpoints fully tested with Postman
- `.env` is excluded from the repository for security
- `.env.example` is provided as a configuration template
- Email verification supports resend functionality
- Soft delete + restore implemented without admin
- JWT authentication secured
- Clean REST API design
- Exam-ready project
