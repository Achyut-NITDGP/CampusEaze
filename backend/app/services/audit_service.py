from ..models.audit_log import AuditLog


def log(db, actor_id, action, entity_type, entity_id, detail=""):
    """Append an audit entry (caller commits so it lands in the same transaction as the change)."""
    db.add(AuditLog(actor_id=actor_id, action=action, entity_type=entity_type, entity_id=entity_id, detail=detail))
