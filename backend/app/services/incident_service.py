from sqlalchemy import or_

from ..core.exceptions import err
from ..core.permissions import STAFF, can_review, managed_ids
from ..models.booking import Booking
from ..models.incident import Incident
from ..repositories import booking_repository as bookings, resource_repository as resources
from ..repositories.user_repository import name_of
from ..utils.validators import row
from . import audit_service as audit
from .notification_service import notify, notify_staff

ORDER = {"open": 0, "investigating": 1, "resolved": 2, "closed": 3}


def view(db, i):
    b = bookings.get(db, i.booking_id)
    return row(i, resource_name=resources.get(db, b.resource_id).name, booked_by=name_of(db, b.user_id), reporter_name=name_of(db, i.reported_by))


def open_incident(db, b, reported_by, kind, description, evidence=None):
    i = Incident(booking_id=b.id, reported_by=reported_by, kind=kind, description=description, evidence_urls=",".join(evidence or []))
    db.add(i)
    db.flush()
    r = resources.get(db, b.resource_id)
    notify(db, r.owner_id, f"A {kind} incident was opened for {r.name} (booking #{b.id}).", "incident")
    notify_staff(db, f"A {kind} incident needs review: {r.name}, booking #{b.id}.", "incident")
    audit.log(db, reported_by, "incident.opened", "incident", i.id, kind)
    audit.log(db, reported_by, "booking.incident_opened", "booking", b.id, kind)
    return i


def settle(db, b):
    """A disputed booking completes once none of its incidents are still open."""
    if b.status == "disputed" and not db.query(Incident).filter(Incident.booking_id == b.id, Incident.status.in_(("open", "investigating"))).count():
        b.status = "completed"
        audit.log(db, None, "booking.completed", "booking", b.id, "all incidents resolved")


def create(db, user, data):
    b = bookings.get(db, data.booking_id)
    r = resources.get(db, b.resource_id)
    if b.user_id != user.id and not can_review(user, r):
        raise err(403, "You can only report issues on your own bookings or resources")
    if b.status not in ("approved", "checked_in", "completed", "disputed"):
        raise err(409, "Incidents can be reported once a booking is approved")
    if data.kind in ("damage", "dispute") and b.status == "completed":
        b.status = "disputed"
    i = open_incident(db, b, user.id, data.kind, data.description.strip(), data.evidence_urls)
    db.commit()
    return i


def list_for(db, user, scope, status=None):
    q = db.query(Incident).join(Booking, Incident.booking_id == Booking.id)
    if scope == "managed" and user.role in STAFF:
        ids = managed_ids(db, user)
        if ids is not None:
            q = q.filter(Booking.resource_id.in_(ids))
    else:
        q = q.filter(or_(Booking.user_id == user.id, Incident.reported_by == user.id))
    if status:
        q = q.filter(Incident.status == status)
    return [view(db, i) for i in q.order_by(Incident.id.desc()).all()]


def update(db, staff, iid, data):
    i = db.get(Incident, iid)
    if not i:
        raise err(404, "Incident not found")
    b = bookings.get(db, i.booking_id, lock=True)
    r = resources.get(db, b.resource_id)
    if not can_review(staff, r):
        raise err(403, "Only the owner or an admin can update this incident")
    if ORDER[data.status] <= ORDER[i.status]:
        raise err(409, "Incidents only move forward: open, investigating, resolved, closed")
    findings, resolution = data.findings or i.findings, data.resolution or i.resolution
    if data.status in ("resolved", "closed") and not (findings and resolution):
        raise err(400, "Record findings and a resolution before resolving")
    i.status, i.findings, i.resolution = data.status, findings, resolution
    if data.status in ("resolved", "closed"):
        i.resolved_by = staff.id
    for uid in {b.user_id, i.reported_by} - {None}:
        notify(db, uid, f"Incident #{i.id} on {r.name} is now {i.status}.", "incident")
    audit.log(db, staff.id, f"incident.{i.status}", "incident", i.id, resolution[:200])
    db.flush()
    settle(db, b)
    db.commit()
    return i
