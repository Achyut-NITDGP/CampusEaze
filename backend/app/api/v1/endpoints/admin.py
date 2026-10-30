from datetime import timedelta

from fastapi import APIRouter, Depends

from ....config import LATE_GRACE_MINUTES
from ....core.dependencies import require
from ....core.permissions import ADMINS, STAFF, managed_ids
from ....database import get_db
from ....models.audit_log import AuditLog
from ....models.booking import Booking
from ....models.incident import Incident
from ....models.notification import Notification
from ....models.resource import Resource
from ....repositories.user_repository import name_of
from ....services import audit_service as audit
from ....services.notification_service import notify
from ....utils.validators import now, row

router = APIRouter()


def _resources(db, u):
    q = db.query(Resource)
    ids = managed_ids(db, u)
    return q if ids is None else q.filter(Resource.id.in_(ids))


def _bookings(db, u):
    q = db.query(Booking)
    ids = managed_ids(db, u)
    return q if ids is None else q.filter(Booking.resource_id.in_(ids))


@router.get("/stats")
def stats(db=Depends(get_db), u=Depends(require(*STAFF))):
    since = now() - timedelta(days=30)
    util = []
    for r in _resources(db, u).all():
        bs = db.query(Booking).filter(Booking.resource_id == r.id, Booking.status.in_(("checked_in", "completed", "disputed")), Booking.start_time >= since).all()
        hours = sum((b.end_time - b.start_time).total_seconds() for b in bs) / 3600
        util.append({"id": r.id, "resource": r.name, "hours_booked": round(hours, 1), "utilisation_pct": round(100 * hours / (12 * 30), 1)})
    ids = managed_ids(db, u)
    inc = db.query(Incident).join(Booking, Incident.booking_id == Booking.id).filter(Incident.status.in_(("open", "investigating")))
    if ids is not None:
        inc = inc.filter(Booking.resource_id.in_(ids))
    return {
        "pending_requests": _bookings(db, u).filter(Booking.status == "pending").count(),
        "upcoming_bookings": _bookings(db, u).filter(Booking.status == "approved", Booking.start_time > now()).count(),
        "unresolved_incidents": inc.count(),
        "overdue_returns": _bookings(db, u).filter(Booking.status == "checked_in", Booking.end_time < now()).count(),
        "utilisation": util,
    }


@router.get("/inventory")
def inventory(db=Depends(get_db), u=Depends(require(*STAFF))):
    out = []
    for r in _resources(db, u).order_by(Resource.name):
        cur = db.query(Booking).filter(Booking.resource_id == r.id, Booking.status == "checked_in").first()
        nxt = db.query(Booking).filter(Booking.resource_id == r.id, Booking.status == "approved", Booking.start_time > now()).order_by(Booking.start_time).first()
        out.append(row(r, "description", "rules", current_status="in use" if cur else r.status,
                       current_user=name_of(db, cur.user_id) if cur else None, next_booking=nxt.start_time if nxt else None))
    return out


@router.get("/transactions")
def transactions(db=Depends(get_db), u=Depends(require(*ADMINS))):
    bs = db.query(Booking).filter(Booking.payment_status != "not_required").order_by(Booking.id.desc()).all()
    return [{"id": b.id, "receipt": f"R-{b.id:05d}", "user": name_of(db, b.user_id), "resource": db.get(Resource, b.resource_id).name,
             "amount": b.amount, "payment_status": b.payment_status, "created_at": b.created_at} for b in bs]


@router.get("/audit-logs")
def audit_logs(entity_type: str | None = None, db=Depends(get_db), u=Depends(require(*ADMINS))):
    q = db.query(AuditLog)
    if entity_type:
        q = q.filter(AuditLog.entity_type == entity_type)
    return [row(a, actor_name=name_of(db, a.actor_id)) for a in q.order_by(AuditLog.id.desc()).limit(300)]


@router.post("/overdue-scan")
def overdue_scan(db=Depends(get_db), u=Depends(require(*STAFF))):
    alerts = 0
    cutoff = now() - timedelta(minutes=LATE_GRACE_MINUTES)
    for b in _bookings(db, u).filter(Booking.status == "checked_in", Booking.end_time < cutoff):
        msg = f"Booking #{b.id} is overdue. Please return the resource."
        if db.query(Notification).filter_by(user_id=b.user_id, message=msg).first():
            continue
        r = db.get(Resource, b.resource_id)
        notify(db, b.user_id, msg, "overdue")
        notify(db, r.owner_id, f"{name_of(db, b.user_id)} has not returned {r.name} (booking #{b.id}).", "overdue")
        alerts += 1
    audit.log(db, u.id, "overdue.scan", "booking", 0, f"{alerts} alerts")
    db.commit()
    return {"alerts": alerts}
