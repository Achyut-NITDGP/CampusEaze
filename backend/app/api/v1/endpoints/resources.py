from datetime import date

from fastapi import APIRouter, Depends

from ....core.dependencies import current_user, require
from ....core.permissions import STAFF, managed_ids
from ....database import get_db
from ....models.resource import Resource, ResourceAvailability
from ....repositories import resource_repository, user_repository
from ....schemas.resource import BlockIn, ResourceIn
from ....services import resource_service
from ....utils.validators import now, row

router = APIRouter()


@router.get("")
def search(q: str | None = None, category: str | None = None, location: str | None = None, max_price: float | None = None,
           day: date | None = None, db=Depends(get_db), _=Depends(current_user)):
    return [row(r) for r in resource_service.search(db, q, category, location, max_price, day)]


@router.get("/managed")
def managed(db=Depends(get_db), u=Depends(require(*STAFF))):
    q = db.query(Resource)
    ids = managed_ids(db, u)
    if ids is not None:
        q = q.filter(Resource.id.in_(ids))
    return [row(r) for r in q.order_by(Resource.name)]


@router.get("/{rid}")
def detail(rid: int, db=Depends(get_db), _=Depends(current_user)):
    r = resource_repository.get(db, rid)
    blocks = db.query(ResourceAvailability).filter(ResourceAvailability.resource_id == rid, ResourceAvailability.end_time > now()).order_by(ResourceAvailability.start_time)
    return row(r, owner_name=user_repository.name_of(db, r.owner_id), blocks=[row(b) for b in blocks])


@router.get("/{rid}/slots")
def slots(rid: int, day: date, db=Depends(get_db), _=Depends(current_user)):
    resource_repository.get(db, rid)
    return resource_service.slots(db, rid, day)


@router.post("", status_code=201)
def create(data: ResourceIn, db=Depends(get_db), u=Depends(require(*STAFF))):
    return row(resource_service.create(db, u, data))


@router.put("/{rid}")
def update(rid: int, data: ResourceIn, db=Depends(get_db), u=Depends(require(*STAFF))):
    return row(resource_service.update(db, u, rid, data))


@router.post("/{rid}/blocks", status_code=201)
def block(rid: int, data: BlockIn, db=Depends(get_db), u=Depends(require(*STAFF))):
    return row(resource_service.block(db, u, rid, data))
