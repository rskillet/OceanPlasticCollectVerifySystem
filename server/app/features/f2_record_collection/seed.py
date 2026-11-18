"""Feature 2 - seed data, called by app/seed.py (after users and boats).

Demo records in all three statuses with a sample scale photo each (NFR-21).
Written in the shared schema PR (team decision D11) - owner please review.

The records are spread over the last 60 days in Thailand time, so "today",
"this month" and "this year" totals all show something. A fixed random seed
gives the same demo data on every computer.
"""

import random
from datetime import timedelta

from sqlmodel import Session, select

from app.core.clock import THAILAND, thailand_day_start, utc_now
from app.features.f1_accounts.models import User
from app.features.f2_record_collection.models import MATERIALS, Photo, Record, make_record_number
from app.features.f5_fleet_boats.models import Boat

REJECT_REASONS = [
    "The scale reading is not visible in the photo.",
    "The weight does not match the photo.",
    "The photo shows a different boat.",
]


def scale_photo(weight_kg: float) -> bytes:
    """A small SVG picture of a digital scale showing the weight (demo photo)."""
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="640" height="480" viewBox="0 0 640 480">
<rect width="640" height="480" fill="#0f2a33"/>
<rect x="120" y="140" width="400" height="200" rx="16" fill="#09181d" stroke="#2c4a54" stroke-width="4"/>
<text x="320" y="185" fill="#7fa3ad" font-family="Arial" font-size="18" text-anchor="middle" letter-spacing="3">DEMO SCALE PHOTO</text>
<text x="320" y="275" fill="#7ee0b0" font-family="Courier New, monospace" font-size="84" font-weight="bold" text-anchor="middle">{weight_kg:g}</text>
<text x="320" y="315" fill="#7fa3ad" font-family="Arial" font-size="22" text-anchor="middle">kg recorded</text>
</svg>"""
    return svg.encode()


def seed(session: Session) -> None:
    rng = random.Random(525)
    crews = session.exec(
        select(User).where(User.username.in_(["mreyes", "lnovak", "jperet", "tiversen"])).order_by(User.id)
    ).all()
    reviewer = session.exec(select(User).where(User.username == "smendes")).one()
    boats = session.exec(select(Boat).order_by(Boat.id)).all()

    now = utc_now()
    # Thailand 09:00 today, as UTC
    today_9am = now.astimezone(THAILAND).replace(hour=9, minute=0, second=0, microsecond=0)

    plans = []  # (days_ago, crew)
    for days_ago in range(60, 0, -2):
        plans.append((days_ago, rng.choice(crews)))
    marco = next(c for c in crews if c.username == "mreyes")
    plans += [(0, marco), (0, marco)]  # two pending records today for the crew home screen

    for days_ago, crew in plans:
        recorded_at = today_9am - timedelta(days=days_ago) + timedelta(minutes=rng.randint(0, 8 * 60))
        if recorded_at > now:  # early morning: keep today's records inside today
            recorded_at = max(thailand_day_start(now), now - timedelta(minutes=rng.randint(5, 60)))
        weight = float(rng.choice(range(40, 600, 5)))
        record = Record(
            boat_id=rng.choice(boats).id,
            crew_id=crew.id,
            weight_kg=weight,
            material=rng.choice(MATERIALS),
            latitude=round(8.75 + rng.uniform(-0.05, 0.05), 5),  # around Phuket
            longitude=round(98.23 + rng.uniform(-0.05, 0.05), 5),
            gps_accuracy_m=round(rng.uniform(3, 12), 1),
            recorded_at=recorded_at,
            created_at=recorded_at + timedelta(minutes=rng.randint(1, 30)),
        )
        if days_ago >= 6:  # older records were already decided by the sponsor
            record.status = "REJECTED" if rng.random() < 0.15 else "VERIFIED"
            record.reviewed_by = reviewer.id
            record.reviewed_at = recorded_at + timedelta(hours=rng.randint(2, 30))
            if record.status == "REJECTED":
                record.reason = rng.choice(REJECT_REASONS)
        session.add(record)
        session.flush()  # the id exists now
        record.record_number = make_record_number(record.id)
        data = scale_photo(weight)
        session.add(Photo(record_id=record.id, content_type="image/svg+xml", size_bytes=len(data), data=data))
    session.flush()
