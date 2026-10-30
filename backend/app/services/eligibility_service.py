from ..models.eligibility import EligibilityRecord


def issues(db, user, resource) -> list[str]:
    out = []
    if resource.requires_verification and user.verification_status != "verified":
        out.append("Your identity is not verified yet. Upload an ID document on your profile.")
    q = resource.required_qualification
    if q and not db.query(EligibilityRecord).filter_by(user_id=user.id, requirement_type=q, status="verified").first():
        out.append(f"A verified qualification is required: {q}")
    return out
