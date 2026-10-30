"""Conflict detection, fair-use limits, waiting list and advisory resource matching.

Everything here is deterministic and explainable. It informs people; owners and staff decide.
"""
import re
from collections import Counter
from datetime import datetime, time, timedelta

from ..config import MAX_HOURS_PER_WEEK, MAX_OPEN_BOOKINGS
from ..models.booking import Booking
from ..models.eligibility import EligibilityRecord
from ..models.resource import Resource
from ..repositories import booking_repository as bookings, resource_repository as resources
from ..utils.validators import now, row
from . import audit_service as audit
from .notification_service import notify

HOLDING = ("approved", "checked_in")
OPEN = ("pending", "approved", "checked_in")


def conflicts(db, rid, start, end, exclude_id=None):
    return {"blocked": bool(resources.blocks(db, rid, start, end)), "bookings": bookings.overlapping(db, rid, start, end, HOLDING, exclude_id)}


def busy(db, rid, start, end, exclude_id=None) -> bool:
    c = conflicts(db, rid, start, end, exclude_id)
    return c["blocked"] or bool(c["bookings"])


def fair_use_issues(db, user, start, end) -> list[str]:
    issues = []
    open_n = db.query(Booking).filter(Booking.user_id == user.id, Booking.status.in_(OPEN + ("waitlisted",)), Booking.end_time > now()).count()
    if open_n >= MAX_OPEN_BOOKINGS:
        issues.append(f"Fair-use limit: you can hold at most {MAX_OPEN_BOOKINGS} open bookings at once.")
    wk = datetime.combine(start.date() - timedelta(days=start.weekday()), time.min)
    rows = db.query(Booking).filter(Booking.user_id == user.id, Booking.status.in_(OPEN), Booking.start_time >= wk, Booking.start_time < wk + timedelta(days=7)).all()
    hours = sum((b.end_time - b.start_time).total_seconds() for b in rows) / 3600 + (end - start).total_seconds() / 3600
    if hours > MAX_HOURS_PER_WEEK:
        issues.append(f"Fair-use limit: {MAX_HOURS_PER_WEEK:g} booked hours per week (this request makes {hours:g}).")
    return issues


def waitlist_position(db, b) -> int:
    return db.query(Booking).filter(
        Booking.resource_id == b.resource_id, Booking.status == "waitlisted", Booking.start_time < b.end_time,
        Booking.end_time > b.start_time, Booking.created_at <= b.created_at,
    ).count()


def promote_waitlist(db, rid):
    """First-come-first-served: when a slot frees up, waitlisted requests move back to owner review."""
    for b in db.query(Booking).filter(Booking.resource_id == rid, Booking.status == "waitlisted").order_by(Booking.created_at):
        if b.end_time > now() and not busy(db, rid, b.start_time, b.end_time, b.id):
            b.status = "pending"
            notify(db, b.user_id, "A slot opened up. Your waitlisted request is now with the owner for review.", "waitlist")
            audit.log(db, None, "booking.waitlist_promoted", "booking", b.id)


def recommend(db, user, limit=4):
    """Advisory matching: past categories, purpose keywords and verified qualifications."""
    past = db.query(Booking).filter_by(user_id=user.id).all()
    cats = Counter(db.get(Resource, b.resource_id).category for b in past)
    words = {w for b in past for w in re.findall(r"[a-z]{4,}", b.purpose.lower())}
    quals = {e.requirement_type for e in db.query(EligibilityRecord).filter_by(user_id=user.id, status="verified")}
    scored = []
    for r in db.query(Resource).filter(Resource.status == "active", Resource.owner_id != user.id):
        text = f"{r.name} {r.description}".lower()
        s = 2 * cats[r.category] + sum(w in text for w in words) + (3 if r.required_qualification in quals else 0)
        scored.append((s, r))
    scored.sort(key=lambda x: (-x[0], x[1].name))
    return [row(r, match_score=s) for s, r in scored[:limit]]
