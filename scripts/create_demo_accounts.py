"""Create demo accounts (password: Demo@12345). Demo data only - never use in production."""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "backend"))

from app import models  # noqa: E402,F401
from app.core.security import hash_password  # noqa: E402
from app.database import Base, SessionLocal, engine  # noqa: E402
from app.models.user import User  # noqa: E402

PASSWORD = "Demo@12345"
ACCOUNTS = [
    ("Ada Admin", "admin@demo.edu", "admin", "verified"),
    ("Omar Owner", "owner@demo.edu", "owner", "verified"),
    ("Sana Student", "student@demo.edu", "user", "verified"),
    ("Neel Newcomer", "newcomer@demo.edu", "user", "unverified"),
]


def create_accounts(db):
    for name, email, role, ver in ACCOUNTS:
        if not db.query(User).filter_by(email=email).first():
            db.add(User(name=name, email=email, role=role, verification_status=ver, password_hash=hash_password(PASSWORD)))
    db.commit()


if __name__ == "__main__":
    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        create_accounts(db)
    print("Accounts ready:", ", ".join(a[1] for a in ACCOUNTS), "| password:", PASSWORD)
