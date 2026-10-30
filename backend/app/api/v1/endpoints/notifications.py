from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from ....core.dependencies import current_user, require
from ....core.exceptions import err
from ....core.permissions import ADMINS
from ....database import get_db
from ....models.notification import Notification
from ....models.user import User
from ....services import audit_service as audit
from ....services.notification_service import notify
from ....utils.validators import now, row

router = APIRouter()


class SendIn(BaseModel):
    user_id: int | None = None  # None = everyone
    message: str = Field(min_length=3, max_length=500)


@router.get("")
def mine(db=Depends(get_db), u=Depends(current_user)):
    return [row(n) for n in db.query(Notification).filter_by(user_id=u.id).order_by(Notification.id.desc()).limit(100)]


@router.post("/read-all")
def read_all(db=Depends(get_db), u=Depends(current_user)):
    db.query(Notification).filter(Notification.user_id == u.id, Notification.read_at.is_(None)).update({"read_at": now()})
    db.commit()
    return {"ok": True}


@router.post("/send")
def send(data: SendIn, db=Depends(get_db), actor=Depends(require(*ADMINS))):
    targets = [data.user_id] if data.user_id else [i for (i,) in db.query(User.id).filter(User.active.is_(True))]
    for uid in targets:
        notify(db, uid, data.message, "announcement")
    audit.log(db, actor.id, "notification.sent", "user", data.user_id or 0, data.message[:200])
    db.commit()
    return {"sent": len(targets)}


@router.post("/{nid}/read")
def read(nid: int, db=Depends(get_db), u=Depends(current_user)):
    n = db.get(Notification, nid)
    if not n or n.user_id != u.id:
        raise err(404, "Notification not found")
    n.read_at = now()
    db.commit()
    return row(n)
