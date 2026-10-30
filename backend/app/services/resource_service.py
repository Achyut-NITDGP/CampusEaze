from datetime import datetime, time, timedelta

from sqlalchemy import or_

from ..core.exceptions import err
from ..core.permissions import can_review
from ..models.resource import Resource, ResourceAvailability
from ..repositories import resource_repository as repo
from ..utils.validators import naive
from . import allocation_service as alloc, audit_service as audit

OPEN_HOUR, CLOSE_HOUR = 8, 20


def slots(db, rid, day):
    out = []
    for h in range(OPEN_HOUR, CLOSE_HOUR):
        s = datetime.combine(day, time(h))
        e = s + timedelta(hours=1)
        out.append({"start": s, "end": e, "available": not alloc.busy(db, rid, s, e)})
    return out


def search(db, q=None, category=None, location=None, max_price=None, day=None):
    qs = db.query(Resource).filter(Resource.status == "active")
    if q:
        qs = qs.filter(or_(Resource.name.ilike(f"%{q}%"), Resource.description.ilike(f"%{q}%")))
    if category:
        qs = qs.filter(Resource.category == category)
    if location:
        qs = qs.filter(Resource.location.ilike(f"%{location}%"))
    if max_price is not None:
        qs = qs.filter(Resource.price_per_hour <= max_price)
    items = qs.order_by(Resource.name).all()
    if day:
        items = [r for r in items if any(s["available"] for s in slots(db, r.id, day))]
    return items


def create(db, user, data):
    r = Resource(owner_id=user.id, **data.model_dump())
    db.add(r)
    db.flush()
    audit.log(db, user.id, "resource.created", "resource", r.id, r.name)
    db.commit()
    return r


def update(db, user, rid, data):
    r = repo.get(db, rid)
    if not can_review(user, r):
        raise err(403, "Only the owner or an admin can edit this resource")
    for k, v in data.model_dump().items():
        setattr(r, k, v)
    audit.log(db, user.id, "resource.updated", "resource", r.id, r.status)
    db.commit()
    return r


def block(db, user, rid, data):
    r = repo.get(db, rid)
    if not can_review(user, r):
        raise err(403, "Only the owner or an admin can block slots")
    s, e = naive(data.start_time), naive(data.end_time)
    if e <= s:
        raise err(400, "End must be after start")
    if alloc.conflicts(db, rid, s, e)["bookings"]:
        raise err(409, "Approved bookings overlap this period. Cancel them first.")
    b = ResourceAvailability(resource_id=rid, start_time=s, end_time=e, reason=data.reason)
    db.add(b)
    db.flush()
    audit.log(db, user.id, "resource.slot_blocked", "resource", rid, data.reason)
    db.commit()
    return b
