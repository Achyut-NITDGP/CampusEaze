from ..models.resource import Resource

STAFF = ("owner", "manager", "admin")
ADMINS = ("manager", "admin")


def can_review(user, resource) -> bool:
    """Admins/managers review everything; owners only their own resources."""
    return user.role in ADMINS or (user.role in STAFF and resource.owner_id == user.id)


def managed_ids(db, user):
    """None = unrestricted (manager/admin); otherwise ids of resources the owner controls."""
    if user.role in ADMINS:
        return None
    return [i for (i,) in db.query(Resource.id).filter(Resource.owner_id == user.id)]
