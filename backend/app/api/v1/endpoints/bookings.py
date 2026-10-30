from fastapi import APIRouter, Depends

from ....core.dependencies import current_user, require
from ....core.permissions import STAFF
from ....database import get_db
from ....schemas.booking import BookingIn, DecisionIn
from ....services import booking_service as svc

router = APIRouter()


@router.post("", status_code=201)
def create(data: BookingIn, db=Depends(get_db), u=Depends(current_user)):
    return svc.view(db, svc.create(db, u, data))


@router.get("")
def list_bookings(scope: str = "mine", status: str | None = None, db=Depends(get_db), u=Depends(current_user)):
    return svc.list_for(db, u, scope, status)


@router.get("/{bid}")
def detail(bid: int, db=Depends(get_db), u=Depends(current_user)):
    return svc.detail(db, u, bid)


@router.post("/{bid}/decision")
def decide(bid: int, data: DecisionIn, db=Depends(get_db), u=Depends(require(*STAFF))):
    return svc.view(db, svc.decide(db, u, bid, data.decision, data.reason))


@router.post("/{bid}/cancel")
def cancel(bid: int, db=Depends(get_db), u=Depends(current_user)):
    return svc.view(db, svc.cancel(db, u, bid))
