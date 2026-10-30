"""Seed demo accounts and resources. Run from the repo root: python scripts/seed_demo_data.py"""
import pathlib
import sys
from datetime import datetime, timedelta

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "backend"))

from create_demo_accounts import create_accounts  # noqa: E402
from app.database import Base, SessionLocal, engine  # noqa: E402
from app.models.resource import Resource, ResourceAvailability  # noqa: E402
from app.models.user import User  # noqa: E402

RESOURCES = [
    ("Prusa 3D Printer", "equipment", "Makerspace, Block B", 50, "3D Printer Training", "Fits parts up to 25 cm. Remove prints within 15 minutes of finishing.", "Reliable FDM printer for prototypes."),
    ("Digital Oscilloscope", "equipment", "Electronics Lab 2", 0, None, "Use supplied probes only. Report any crack or loose knob.", "4-channel 200 MHz scope."),
    ("Soldering Station", "equipment", "Electronics Lab 2", 20, None, "Switch off and cool down before returning.", "Temperature-controlled station with fume extractor."),
    ("Seminar Room 204", "space", "Academic Block, 2nd floor", 150, None, "Leave furniture as found. No food near the projector.", "Seats 30, projector and whiteboards."),
    ("Mentoring Hour: Embedded Systems", "service", "Online / Lab 3", 0, None, "Bring a specific question.", "One-hour guidance from a senior researcher."),
]

if __name__ == "__main__":
    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        create_accounts(db)
        owner = db.query(User).filter_by(email="owner@demo.edu").one()
        for name, cat, loc, price, qual, rules, desc in RESOURCES:
            if not db.query(Resource).filter_by(name=name).first():
                db.add(Resource(owner_id=owner.id, name=name, category=cat, location=loc, price_per_hour=price,
                                required_qualification=qual, rules=rules, description=desc, requires_verification=cat != "service"))
        db.flush()
        printer = db.query(Resource).filter_by(name="Prusa 3D Printer").one()
        tomorrow = (datetime.now() + timedelta(days=1)).replace(hour=13, minute=0, second=0, microsecond=0)
        if not db.query(ResourceAvailability).filter_by(resource_id=printer.id).first():
            db.add(ResourceAvailability(resource_id=printer.id, start_time=tomorrow, end_time=tomorrow + timedelta(hours=2), reason="Nozzle maintenance"))
        db.commit()
    print("Seeded demo data.")
