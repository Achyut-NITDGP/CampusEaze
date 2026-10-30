from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from ..database import get_db
from ..models.user import User
from .exceptions import err
from .security import decode_token

oauth2 = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def current_user(token: str = Depends(oauth2), db=Depends(get_db)) -> User:
    try:
        uid = int(decode_token(token)["sub"])
    except Exception:
        raise err(401, "Session expired - please sign in again")
    u = db.get(User, uid)
    if not u or not u.active:
        raise err(401, "Account unavailable")
    return u


def require(*roles):
    def dep(u: User = Depends(current_user)) -> User:
        if u.role not in roles:
            raise err(403, "You do not have permission to do this")
        return u
    return dep
