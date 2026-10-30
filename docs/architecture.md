# Architecture
Modular monolith: React SPA → REST (`/api/v1`) → FastAPI endpoints → services → repositories → SQLAlchemy → PostgreSQL.
- **Endpoints** are thin: auth, role check, call a service.
- **Services** hold the rules (eligibility, fair use, conflicts, state transitions) and write audit and notification rows in the same transaction.
- **Repositories** own queries and row locks (`SELECT … FOR UPDATE` on the resource while booking/approving, so two requests cannot take the same slot on PostgreSQL).
- **Times** are naive campus-local datetimes end to end. Add timezone handling before multi-site use.
- **Payments** are simulated: `payment_status` goes paid → refunded on rejection or cancellation. Plug a gateway into `booking_service`.
- **AI use**: `allocation_service` provides explainable matching (history, keywords, qualifications) and conflict detection. They advise; approvals, verification and incident outcomes are always made by people.
