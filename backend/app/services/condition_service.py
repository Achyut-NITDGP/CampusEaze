from datetime import timedelta

from ..config import CHECKIN_EARLY_MINUTES, LATE_GRACE_MINUTES
from ..core.exceptions import err
from ..core.permissions import can_review, managed_ids
from ..models.booking import Booking
from ..models.condition_report import ConditionReport
from ..models.incident import Incident
from ..repositories import booking_repository as bookings, resource_repository as resources
from ..repositories.user_repository import name_of
from ..utils.validators import now, row
from . import audit_service as audit, incident_service as incidents
from .notification_service import notify


def _own_booking(db, user, bid, status):
    b = bookings.get(db, bid, lock=True)
    if b.user_id != user.id:
        raise err(403, "Only the person who booked can do this")
    if b.status != status:
        raise err(409, f"This booking is {b.status}; it must be {status}")
    return b


def _report(db, b, user, kind, data):
    rep = ConditionReport(
        booking_id=b.id, report_type=kind, condition_notes=data.condition_notes, checklist_ok=data.checklist_ok,
        damage_reported=data.damage_reported, photo_urls=",".join(data.photo_urls), created_by=user.id,
        flagged=(not data.checklist_ok) or data.damage_reported,
    )
    db.add(rep)
    db.flush()
    return rep


def check_in(db, user, bid, data):
    b = _own_booking(db, user, bid, "approved")
    if now() < b.start_time - timedelta(minutes=CHECKIN_EARLY_MINUTES):
        raise err(409, "Check-in is not open yet")
    if now() > b.end_time:
        raise err(409, "This booking window has ended")
    rep = _report(db, b, user, "checkin", data)
    b.status = "checked_in"
    r = resources.get(db, b.resource_id)
    if rep.flagged:  # protects the user: pre-existing damage is on record before use
        incidents.open_incident(db, b, user.id, "damage", "Reported at check-in: " + (data.condition_notes or "checklist not satisfied"), data.photo_urls)
    notify(db, r.owner_id, f"{user.name} checked in to {r.name}.", "handover")
    audit.log(db, user.id, "booking.checked_in", "booking", b.id, data.condition_notes[:200])
    db.commit()
    return rep


def check_out(db, user, bid, data):
    b = _own_booking(db, user, bid, "checked_in")
    rep = _report(db, b, user, "checkout", data)
    b.status = "disputed" if rep.flagged else "completed"
    if rep.flagged:
        incidents.open_incident(db, b, None, "damage", "Flagged at return: " + (data.condition_notes or "checklist not satisfied"), data.photo_urls)
    late = (now() - b.end_time).total_seconds() / 60
    if late > LATE_GRACE_MINUTES:
        incidents.open_incident(db, b, None, "delay", f"Returned {int(late)} minutes after the booked end time")
    r = resources.get(db, b.resource_id)
    notify(db, r.owner_id, f"{user.name} returned {r.name}" + (" - flagged for review." if rep.flagged else "."), "handover")
    notify(db, user.id, f"Return of {r.name} recorded." + (" It was flagged for human review." if rep.flagged else ""), "handover")
    audit.log(db, user.id, "booking.checked_out", "booking", b.id, "flagged" if rep.flagged else "ok")
    db.commit()
    return rep


def list_reports(db, user, only_unreviewed_flags):
    q = db.query(ConditionReport).join(Booking, ConditionReport.booking_id == Booking.id)
    ids = managed_ids(db, user)
    if ids is not None:
        q = q.filter(Booking.resource_id.in_(ids))
    if only_unreviewed_flags:
        q = q.filter(ConditionReport.flagged.is_(True), ConditionReport.reviewed_by.is_(None))
    out = []
    for rep in q.order_by(ConditionReport.id.desc()).all():
        b = bookings.get(db, rep.booking_id)
        out.append(row(rep, resource_name=resources.get(db, b.resource_id).name, user_name=name_of(db, b.user_id)))
    return out


def review(db, reviewer, rid, data):
    rep = db.get(ConditionReport, rid)
    if not rep:
        raise err(404, "Report not found")
    b = bookings.get(db, rep.booking_id, lock=True)
    r = resources.get(db, b.resource_id)
    if not can_review(reviewer, r):
        raise err(403, "Only the owner or an admin can review this report")
    if rep.reviewed_by:
        raise err(409, "This report was already reviewed")
    rep.reviewed_by, rep.review_outcome, rep.review_note = reviewer.id, data.outcome, data.note
    if data.outcome == "cleared":  # a human cleared the automatic flag
        for i in db.query(Incident).filter(Incident.booking_id == b.id, Incident.kind == "damage", Incident.reported_by.is_(None), Incident.status.in_(("open", "investigating"))):
            i.status, i.findings, i.resolution, i.resolved_by = "resolved", f"Reviewed and cleared: {data.note}", "No damage confirmed", reviewer.id
        db.flush()
        incidents.settle(db, b)
    notify(db, b.user_id, f"Your {rep.report_type} report for {r.name} was reviewed: {data.outcome.replace('_', ' ')}.", "handover")
    audit.log(db, reviewer.id, f"report.{data.outcome}", "booking", b.id, data.note)
    db.commit()
    return rep
