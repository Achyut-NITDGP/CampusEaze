from fastapi import APIRouter, Depends

from ....core.dependencies import current_user, require
from ....core.permissions import STAFF
from ....database import get_db
from ....schemas.incident import IncidentIn, IncidentUpdate
from ....services import incident_service as svc

router = APIRouter()


@router.post("", status_code=201)
def create(data: IncidentIn, db=Depends(get_db), u=Depends(current_user)):
    return svc.view(db, svc.create(db, u, data))


@router.get("")
def list_incidents(scope: str = "mine", status: str | None = None, db=Depends(get_db), u=Depends(current_user)):
    return svc.list_for(db, u, scope, status)


@router.patch("/{iid}")
def update(iid: int, data: IncidentUpdate, db=Depends(get_db), u=Depends(require(*STAFF))):
    return svc.view(db, svc.update(db, u, iid, data))
