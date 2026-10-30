from fastapi import APIRouter, Depends

from ....core.dependencies import current_user, require
from ....core.exceptions import err
from ....core.permissions import ADMINS
from ....database import get_db
from ....models.eligibility import EligibilityRecord
from ....repositories import resource_repository, user_repository
from ....schemas.user import EligibilityIn, EligibilityReview
from ....services import audit_service as audit, eligibility_service
from ....services.notification_service import notify
from ....utils.validators import row

router = APIRouter()


@router.get("/me")
def mine(db=Depends(get_db), u=Depends(current_user)):
    return [row(e) for e in db.query(EligibilityRecord).filter_by(user_id=u.id).order_by(EligibilityRecord.id.desc())]


@router.get("/check")
def check(resource_id: int, db=Depends(get_db), u=Depends(current_user)):
    issues = eligibility_service.issues(db, u, resource_repository.get(db, resource_id))
    return {"ok": not issues, "issues": issues}


@router.post("", status_code=201)
def submit(data: EligibilityIn, db=Depends(get_db), u=Depends(current_user)):
    if data.document_url and not data.document_url.startswith("/uploads/"):
        raise err(400, "Upload the document first, then submit it")
    rec = EligibilityRecord(user_id=u.id, requirement_type=data.requirement_type.strip(), document_url=data.document_url)
    db.add(rec)
    db.flush()
    if rec.requirement_type.lower() == "identity" and u.verification_status != "verified":
        u.verification_status = "pending"
    audit.log(db, u.id, "eligibility.submitted", "user", u.id, rec.requirement_type)
    db.commit()
    return row(rec)


@router.get("")
def pending(status: str = "pending", db=Depends(get_db), _=Depends(require(*ADMINS))):
    recs = db.query(EligibilityRecord).filter_by(status=status).order_by(EligibilityRecord.id)
    return [row(e, user_name=user_repository.name_of(db, e.user_id)) for e in recs]


@router.patch("/{eid}")
def review(eid: int, data: EligibilityReview, db=Depends(get_db), actor=Depends(require(*ADMINS))):
    rec = db.get(EligibilityRecord, eid)
    if not rec:
        raise err(404, "Record not found")
    rec.status, rec.verified_by = data.status, actor.id
    if rec.requirement_type.lower() == "identity":
        user_repository.get(db, rec.user_id).verification_status = data.status
    notify(db, rec.user_id, f"Your {rec.requirement_type} submission was {data.status}.", "verification")
    audit.log(db, actor.id, f"eligibility.{data.status}", "user", rec.user_id, rec.requirement_type)
    db.commit()
    return row(rec)
