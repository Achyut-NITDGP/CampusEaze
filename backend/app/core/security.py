import hashlib
import hmac
import os
from datetime import datetime, timedelta, timezone

import jwt

from ..config import SECRET_KEY, TOKEN_MINUTES


def hash_password(p: str) -> str:
    salt = os.urandom(16)
    return salt.hex() + "$" + hashlib.pbkdf2_hmac("sha256", p.encode(), salt, 200_000).hex()


def verify_password(p: str, stored: str) -> bool:
    salt, digest = stored.split("$")
    return hmac.compare_digest(hashlib.pbkdf2_hmac("sha256", p.encode(), bytes.fromhex(salt), 200_000).hex(), digest)


def create_token(uid: int, role: str) -> str:
    exp = datetime.now(timezone.utc) + timedelta(minutes=TOKEN_MINUTES)
    return jwt.encode({"sub": str(uid), "role": role, "exp": exp}, SECRET_KEY, algorithm="HS256")


def decode_token(t: str) -> dict:
    return jwt.decode(t, SECRET_KEY, algorithms=["HS256"])
