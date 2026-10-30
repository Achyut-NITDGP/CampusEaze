from datetime import timedelta

from fastapi import HTTPException

from ..core.exceptions import err
from ..core.permissions import STAFF, can_review, managed_ids
from ..models.audit_log import AuditLog
from ..models.booking import Booking, BookingDecision
from ..models.condition_report import ConditionReport
from ..models.incident import Incident
from ..repositories import booking_repository as repo, resource_repository as res_repo
from ..repositories.user_repository import name_of
from ..utils.validators import naive, now, row
from . import allocation_service as alloc, audit_service as audit, eligibility_service as elig
from .notification_service import notify


def view(db, b):
    r = res_repo.get(db, b.resource_id)
    pending = b.status in ("pending", "waitlisted")
    return row(
        b, resource_name=r.name, owner_id=r.owner_id, user_name=name_of(db, b.user_id),
        waitlist_position=alloc.waitlist_position(db, b) if b.status == "waitlisted" else None,
        has_conflict=alloc.busy(db, b.resource_id, b.start_time, b.end_time, b.id) if pending else False,
    )


def create(db, user, data):
    start, end = naive(data.start_time), naive(data.end_time)
    if end <= start:
        raise err(400, "End must be after start")
    if start < now() - timedelta(minutes=5):
        raise err(400, "Start time is in the past")
    if end - start > timedelta(hours=8):
        raise err(400, "Bookings can be at most 8 hours long")
    r = res_repo.get(db, data.resource_id, lock=True)
    if r.status != "active":
        raise err(409, "This resource is not available for booking")
    if r.owner_id == user.id:
        raise err(400, "You cannot book your own resource")
    issues = elig.issues(db, user, r) + alloc.fair_use_issues(db, user, start, end)
    if issues:
        raise HTTPException(422, {"message": "This booking is not allowed yet", "issues": issues})
    c = alloc.conflicts(db, r.id, start, end)
    if c["blocked"]:
        raise err(409, "The owner has blocked that time")
    status = "waitlisted" if c["bookings"] else "pending"
    amount = round((end - start).total_seconds() / 3600 * r.price_per_hour, 2)
    b = Booking(resource_id=r.id, user_id=user.id, start_time=start, end_time=end, purpose=data.purpose.strip(),
                status=status, amount=amount, payment_status="paid" if amount > 0 else "not_required")
    db.add(b)
    db.flush()
    notify(db, user.id, f"Your request for {r.name} is {'on the waiting list' if status == 'waitlisted' else 'with the owner for review'}.", "booking")
    notify(db, r.owner_id, f"New {status} request for {r.name} from {user.name}.", "booking")
    audit.log(db, user.id, "booking.requested", "booking", b.id, status)
    db.commit()
    return b


def decide(db, reviewer, bid, decision, reason):
    b = repo.get(db, bid, lock=True)
    r = res_repo.get(db, b.resource_id, lock=True)
    if not can_review(reviewer, r):
        raise err(403, "Only the resource owner or an admin can decide on this request")
    if b.status not in ("pending", "waitlisted"):
        raise err(409, f"This booking is already {b.status}")
    reason = (reason or "").strip()
    if decision != "approve" and not reason:
        raise err(400, "Please record a reason for this decision")
    if decision == "approve":
        if alloc.busy(db, r.id, b.start_time, b.end_time, b.id):  # re-check under lock
            raise err(409, "That slot is no longer available")
        new = "approved"
    else:
        new = "rejected" if decision == "reject" else "waitlisted"
    if new == "rejected" and b.payment_status == "paid":
        b.payment_status = "refunded"
    b.status = new
    db.add(BookingDecision(booking_id=b.id, reviewer_id=reviewer.id, decision=decision, reason=reason))
    notify(db, b.user_id, f"Your request for {r.name} was {new}." + (f" Reason: {reason}" if reason else ""), "booking")
    audit.log(db, reviewer.id, f"booking.{new}", "booking", b.id, reason)
    db.commit()
    return b


def cancel(db, user, bid):
    b = repo.get(db, bid, lock=True)
    r = res_repo.get(db, b.resource_id)
    if user.id != b.user_id and not can_review(user, r):
        raise err(403, "You cannot cancel this booking")
    if b.status not in ("pending", "waitlisted", "approved"):
        raise err(409, f"A {b.status} booking cannot be cancelled")
    b.status = "cancelled"
    if b.payment_status == "paid":
        b.payment_status = "refunded"
    notify(db, r.owner_id if user.id == b.user_id else b.user_id, f"Booking #{b.id} for {r.name} was cancelled.", "booking")
    audit.log(db, user.id, "booking.cancelled", "booking", b.id)
    db.flush()
    alloc.promote_waitlist(db, r.id)
    db.commit()
    return b


def list_for(db, user, scope, status=None):
    q = db.query(Booking)
    if scope == "managed" and user.role in STAFF:
        ids = managed_ids(db, user)
        if ids is not None:
            q = q.filter(Booking.resource_id.in_(ids))
    else:
        q = q.filter(Booking.user_id == user.id)
    if status:
        q = q.filter(Booking.status == status)
    return [view(db, b) for b in q.order_by(Booking.start_time.desc()).all()]


def detail(db, user, bid):
    b = repo.get(db, bid)
    r = res_repo.get(db, b.resource_id)
    if b.user_id != user.id and not can_review(user, r):
        raise err(403, "You cannot view this booking")
    logs = db.query(AuditLog).filter(AuditLog.entity_type == "booking", AuditLog.entity_id == b.id).order_by(AuditLog.timestamp, AuditLog.id)
    return {
        **view(db, b),
        "timeline": [row(a, actor_name=name_of(db, a.actor_id)) for a in logs],
        "decisions": [row(d, reviewer_name=name_of(db, d.reviewer_id)) for d in db.query(BookingDecision).filter_by(booking_id=b.id)],
        "reports": [row(x) for x in db.query(ConditionReport).filter_by(booking_id=b.id).order_by(ConditionReport.id)],
        "incidents": [row(i) for i in db.query(Incident).filter_by(booking_id=b.id)],
    }
