# API
Interactive docs: `http://localhost:8000/docs`. All routes are under `/api/v1` and need a Bearer token except `/auth/register` and `/auth/login`.

| Area | Routes |
|---|---|
| auth | `POST /auth/register`, `POST /auth/login`, `GET /auth/me` |
| users | `GET /users/me/dashboard`, `PATCH /users/me`, `GET /users`, `PATCH /users/{id}` |
| resources | `GET /resources`, `GET /resources/managed`, `GET/PUT /resources/{id}`, `GET /resources/{id}/slots`, `POST /resources`, `POST /resources/{id}/blocks` |
| bookings | `POST /bookings`, `GET /bookings?scope=mine\|managed`, `GET /bookings/{id}`, `POST /bookings/{id}/decision`, `POST /bookings/{id}/cancel` |
| eligibility | `GET /eligibility/me`, `GET /eligibility/check`, `POST /eligibility`, `GET/PATCH /eligibility` (staff) |
| handover | `POST /handover/upload`, `POST /handover/{id}/check-in`, `POST /handover/{id}/check-out`, `GET /handover/reports`, `POST /handover/reports/{id}/review` |
| incidents | `POST /incidents`, `GET /incidents?scope=`, `PATCH /incidents/{id}` |
| notifications | `GET /notifications`, `POST /notifications/read-all`, `POST /notifications/{id}/read`, `POST /notifications/send` |
| admin | `GET /admin/stats`, `/admin/inventory`, `/admin/transactions`, `/admin/audit-logs`, `POST /admin/overdue-scan` |
