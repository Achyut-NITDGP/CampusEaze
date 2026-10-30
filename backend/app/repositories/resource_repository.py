from ..core.exceptions import err
from ..models.resource import Resource, ResourceAvailability


def get(db, rid, lock=False):
    q = db.query(Resource).filter(Resource.id == rid)
    r = (q.with_for_update() if lock else q).first()  # row lock prevents double booking on PostgreSQL
    if not r:
        raise err(404, "Resource not found")
    return r


def blocks(db, rid, start, end):
    return db.query(ResourceAvailability).filter(
        ResourceAvailability.resource_id == rid, ResourceAvailability.start_time < end, ResourceAvailability.end_time > start
    ).all()
