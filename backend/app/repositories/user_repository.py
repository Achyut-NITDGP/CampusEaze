from ..core.exceptions import err
from ..models.user import User


def get(db, uid):
    u = db.get(User, uid)
    if not u:
        raise err(404, "User not found")
    return u


def by_email(db, email):
    return db.query(User).filter(User.email == email).first()


def name_of(db, uid) -> str:
    u = db.get(User, uid) if uid else None
    return u.name if u else "System"
