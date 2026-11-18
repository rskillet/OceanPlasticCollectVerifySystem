"""Feature 5 - seed data, called by app/seed.py (after users, before records).

Demo boats from NFR-21 - the same four boats as the F5 mock data.
Written in the shared schema PR (team decision D11) - owner please review.
"""

from sqlmodel import Session

from app.features.f5_fleet_boats.models import Boat

DEMO_BOATS = [
    # (code, name, capacity_kg)
    ("HC-14", "Harbor Cleaner", 1800),
    ("SH-02", "Sea Harvest", 2400),
    ("RM-07", "River Mouth", 900),
    ("SL-03", "Shoreline Team A", 400),
]


def seed(session: Session) -> None:
    for code, name, capacity_kg in DEMO_BOATS:
        session.add(Boat(code=code, name=name, capacity_kg=capacity_kg, active=True))
    session.flush()
