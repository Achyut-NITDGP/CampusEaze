from ..core.exceptions import err
from ..models.booking import Booking


def get(db, bid, lock=False):
    q = db.query(Booking).filter(Booking.id == bid)
    b = (q.with_for_update() if lock else q).first()
    if not b:
        raise err(404, "Booking not found")
    return b


def overlapping(db, rid, start, end, statuses, exclude_id=None):
    q = db.query(Booking).filter(Booking.resource_id == rid, Booking.status.in_(statuses), Booking.start_time < end, Booking.end_time > start)
    if exclude_id:
        q = q.filter(Booking.id != exclude_id)
    return q.all()
