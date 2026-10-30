# Unlock: Underused Equipment and Spaces

A resource-sharing platform for colleges, labs and communities. Full lifecycle: list, discover, verify, request, approve or waitlist, check in, return, report incidents, audit.

**Stack:** React + TypeScript (Vite) · FastAPI · SQLAlchemy · PostgreSQL (SQLite for quick local runs)

## Run it

```bash
# Backend (SQLite by default; set DATABASE_URL for PostgreSQL or use docker compose up db)
cd backend && python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cd .. && python scripts/seed_demo_data.py
cd backend && uvicorn app.main:app --reload          # http://localhost:8000/docs

# Frontend
cd frontend && cp .env.example .env && npm install && npm run dev   # http://localhost:5173

# Tests
cd backend && python -m pytest app/tests
```

Demo accounts (password `Demo@12345`): `admin@demo.edu`, `owner@demo.edu`, `student@demo.edu` (identity verified), `newcomer@demo.edu` (unverified).

Check-in opens `CHECKIN_EARLY_MINUTES` (default 60) before the booking starts. For a live demo, set it to `1440` so you can check in to a booking made for tomorrow.

## Demo script (about 5 minutes)

1. Sign in as **student**, open *Prusa 3D Printer*, pick a slot, and see that the booking is blocked (training required).
2. On *Profile*, submit the qualification "3D Printer Training" with a document.
3. Sign in as **admin**, open *Users & verification*, and verify it.
4. As **student**, request the slot again. As **owner**, approve it in *Booking requests*.
5. As **student**, check in with photos, then check out and tick "I noticed damage".
6. As **owner/admin**, review the flagged report in *Handover review* and resolve the incident in the *Incident centre*.
7. Open *Audit logs* to show every decision with who and when.

See `docs/` for architecture, API, schema, flow, security/fairness and testing notes.
