from ..core.exceptions import err
from ..core.security import create_token, hash_password, verify_password
from ..models.user import User
from ..repositories import user_repository as users
from . import audit_service as audit


def register(db, data):
    if data.role not in ("user", "owner"):
        raise err(400, "You can sign up as a user or an owner")
    email = data.email.lower()
    if users.by_email(db, email):
        raise err(409, "That email is already registered")
    u = User(name=data.name.strip(), email=email, password_hash=hash_password(data.password), role=data.role)
    db.add(u)
    db.flush()
    audit.log(db, u.id, "user.registered", "user", u.id, data.role)
    db.commit()
    return u


def login(db, data):
    u = users.by_email(db, data.email.lower())
    if not u or not u.active or not verify_password(data.password, u.password_hash):
        raise err(401, "Invalid email or password")
    return u, create_token(u.id, u.role)
