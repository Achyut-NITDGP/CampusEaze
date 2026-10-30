# Database schema
`users`, `resources`, `resource_availability` (blocked slots), `eligibility_records`, `bookings`, `booking_decisions`, `condition_reports`, `incidents`, `notifications`, `audit_logs`. Foreign keys link every record to its booking, resource and user.
Booking status: `pending → approved → checked_in → completed` with side exits `waitlisted`, `rejected`, `cancelled`, `disputed`.
Decisions, reports and audit rows are never overwritten; reviews add fields, they do not replace history.
Hardening idea for PostgreSQL: add an exclusion constraint (`btree_gist`) on `(resource_id, tstzrange)` for approved bookings as a second line of defence.
