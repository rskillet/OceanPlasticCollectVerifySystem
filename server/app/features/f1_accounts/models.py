"""Feature 1 - SQLModel tables: DM-1 users and DM-4 sessions.

Other features point to users.id (records.crew_id, records.reviewed_by).

Team decision (docs/DECISIONS.md D8): the username and password are stored
in the users table, and the password is stored as plain text. Never return
the password in an API response - UserOut in schemas.py has no password field.
"""

from datetime import datetime

from sqlalchemy import DateTime
from sqlmodel import Field, Relationship, SQLModel

from app.core.clock import utc_now


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(max_length=120)
    email: str = Field(max_length=200, unique=True, index=True)
    username: str = Field(max_length=30, unique=True, index=True)
    password: str = Field(max_length=200)  # plain text (team decision D8)
    role: str = Field(max_length=30)  # CREW_MEMBER | SPONSOR_MANAGEMENT | ADMIN
    status: str = Field(default="PENDING", max_length=20, index=True)  # PENDING | ACTIVE | REJECTED | SUSPENDED
    created_at: datetime = Field(default_factory=utc_now, sa_type=DateTime(timezone=True))

    # one user -> many sessions; deleting a user deletes their sessions
    sessions: list["UserSession"] = Relationship(back_populates="user", cascade_delete=True)


class UserSession(SQLModel, table=True):
    """One signed-in browser. Not called `Session`: that name is sqlmodel.Session."""

    __tablename__ = "sessions"

    # SHA-256 of the cookie value, so the table alone cannot be used to sign in
    id: str = Field(primary_key=True, max_length=64)
    user_id: int = Field(foreign_key="users.id", index=True)
    created_at: datetime = Field(default_factory=utc_now, sa_type=DateTime(timezone=True))
    expires_at: datetime = Field(sa_type=DateTime(timezone=True))

    user: User = Relationship(back_populates="sessions")
