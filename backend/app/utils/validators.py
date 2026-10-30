from datetime import datetime

# All timestamps are naive "campus-local" times (see docs/architecture.md).


def now() -> datetime:
    return datetime.now()


def naive(dt: datetime) -> datetime:
    return dt.replace(tzinfo=None)


def row(obj, *drop, **extra) -> dict:
    """Serialise an ORM row to a dict, dropping sensitive columns and adding computed fields."""
    d = {c.name: getattr(obj, c.name) for c in obj.__table__.columns if c.name not in drop}
    d.update(extra)
    return d
