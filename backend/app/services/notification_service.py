from ..models.notification import Notification
from ..models.user import User


def notify(db, user_id, message, kind="info"):
    db.add(Notification(user_id=user_id, message=message, kind=kind))


def notify_staff(db, message, kind="info"):
    for u in db.query(User).filter(User.role.in_(("manager", "admin")), User.active.is_(True)):
        notify(db, u.id, message, kind)
