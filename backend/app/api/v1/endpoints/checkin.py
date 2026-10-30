from fastapi import APIRouter, Depends, File, UploadFile

from ....core.dependencies import current_user, require
from ....core.permissions import STAFF
from ....database import get_db
from ....schemas.condition_report import ReportIn, ReportReview
from ....services import condition_service as svc
from ....utils.file_storage import save_upload
from ....utils.validators import row

router = APIRouter()


@router.post("/upload")
async def upload(file: UploadFile = File(...), _=Depends(current_user)):
    return {"url": await save_upload(file)}


@router.get("/reports")
def reports(flagged: bool = True, db=Depends(get_db), u=Depends(require(*STAFF))):
    return svc.list_reports(db, u, flagged)


@router.post("/reports/{rid}/review")
def review(rid: int, data: ReportReview, db=Depends(get_db), u=Depends(require(*STAFF))):
    return row(svc.review(db, u, rid, data))


@router.post("/{bid}/check-in")
def check_in(bid: int, data: ReportIn, db=Depends(get_db), u=Depends(current_user)):
    return row(svc.check_in(db, u, bid, data))


@router.post("/{bid}/check-out")
def check_out(bid: int, data: ReportIn, db=Depends(get_db), u=Depends(current_user)):
    return row(svc.check_out(db, u, bid, data))
