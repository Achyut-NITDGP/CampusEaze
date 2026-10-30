from fastapi import APIRouter, Depends

from ....core.dependencies import current_user, require
from ....core.exceptions import err
from ....core.permissions import ADMINS
from ....database import get_db
from ....models.booking import Booking
from ....models.notification import Notification
from ....models.user import User
from ....repositories import user_repository
from ....schemas.user import UserUpdate
from ....services import allocation_service, audit_service as audit, booking_service
from ....utils.validators import now, row

router = APIRouter()


@router.get("/me/dashboard")
def dashboard(db=Depends(get_db), u=Depends(current_user)):
    bs = db.query(Booking).filter(Booking.user_id == u.id).order_by(Booking.start_time).all()
    unread = db.query(Notification).filter(Notification.user_id == u.id, Notification.read_at.is_(None)).count()
    return {
        "upcoming": [booking_service.view(db, b) for b in bs if b.status in ("approved", "checked_in") and b.end_time > now()],
        "pending": [booking_service.view(db, b) for b in bs if b.status in ("pending", "waitlisted")],
        "unread": unread,
        "recommended": allocation_service.recommend(db, u),
    }


@router.patch("/me")
def update_me(data: UserUpdate, db=Depends(get_db), u=Depends(current_user)):
    if data.name:
        u.name = data.name.strip()
        audit.log(db, u.id, "user.profile_updated", "user", u.id)
        db.commit()
    return row(u, "password_hash")


@router.get("")
def list_users(db=Depends(get_db), _=Depends(require(*ADMINS))):
    return [row(u, "password_hash") for u in db.query(User).order_by(User.id)]


@router.patch("/{uid}")
def update_user(uid: int, data: UserUpdate, db=Depends(get_db), actor=Depends(require(*ADMINS))):
    u = user_repository.get(db, uid)
    if u.role == "admin" and actor.role != "admin":
        raise err(403, "Only admins can modify admin accounts")
    changes = data.model_dump(exclude_none=True)
    changes.pop("name", None)
    if "role" in changes and actor.role != "admin":
        raise err(403, "Only admins can change roles")
    if u.id == actor.id and ("role" in changes or changes.get("active") is False):
        raise err(400, "You cannot change your own role or deactivate yourself")
    for k, v in changes.items():
        setattr(u, k, v)
    audit.log(db, actor.id, "user.updated", "user", u.id, str(changes))
    db.commit()
    return row(u, "password_hash")
