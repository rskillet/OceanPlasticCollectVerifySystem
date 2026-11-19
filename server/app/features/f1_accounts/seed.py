"""Feature 1 - seed data: the default admin (FR-1.9) and demo users (NFR-21).

Called by app/seed.py the first time the backend starts with an empty
database. Usernames and passwords are stored in the users table, not in .env
(team decision D8). Every demo account uses the password `password123`.

The users are added in this order, so their ids are 1-8 (tests and the
other features' seed data rely on the usernames, not on the ids).
"""

from datetime import datetime, timedelta, timezone

from sqlmodel import Session

from app.core.clock import utc_now
from app.features.f1_accounts.models import User

DEMO_PASSWORD = "password123"


def _day(text: str) -> datetime:
    return datetime.fromisoformat(text).replace(tzinfo=timezone.utc)


def demo_users() -> list[User]:
    now = utc_now()
    rows = [
        # (name, username, email, role, status, created_at)
        ("Marco Reyes", "mreyes", "m.reyes@opr.org", "CREW_MEMBER", "ACTIVE", _day("2026-03-02T08:00")),
        ("Lea Novak", "lnovak", "l.novak@opr.org", "CREW_MEMBER", "ACTIVE", _day("2026-03-09T08:00")),
        ("Jonas Peret", "jperet", "j.peret@opr.org", "CREW_MEMBER", "ACTIVE", _day("2026-04-14T08:00")),
        ("Tomas Iversen", "tiversen", "t.iversen@opr.org", "CREW_MEMBER", "SUSPENDED", _day("2026-04-20T08:00")),
        ("Amara Osei", "admin", "a.osei@opr.org", "ADMIN", "ACTIVE", _day("2026-01-12T08:00")),
        ("Sofia Mendes", "smendes", "s.mendes@opr.org", "SPONSOR_MANAGEMENT", "ACTIVE", _day("2026-02-03T08:00")),
        ("Elena Vasquez", "evasquez", "e.vasquez@opr.org", "CREW_MEMBER", "PENDING", now - timedelta(hours=2)),
        ("Priya Raman", "praman", "p.raman@nordsea.com", "SPONSOR_MANAGEMENT", "PENDING", now - timedelta(hours=48)),
    ]
    return [
        User(name=name, username=username, email=email, password=DEMO_PASSWORD, role=role, status=status, created_at=created_at)
        for name, username, email, role, status, created_at in rows
    ]


def seed(session: Session) -> None:
    """Add the demo users. app/seed.py commits once all features are seeded."""
    for user in demo_users():
        session.add(user)
        session.flush()  # sends the INSERT now, so ids follow the list order
