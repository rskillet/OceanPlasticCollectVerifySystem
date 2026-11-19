"""Feature 1 - business logic (router functions stay thin).

Data lives in PostgreSQL: the `users` and `sessions` tables (models.py).
Every function receives the request's database session (`db`) from the
router, the same pattern as the ORM lecture: session.add -> session.commit.

Passwords are stored and compared as plain text (team decision D8).
"""

import hashlib
import re
import secrets
from datetime import timedelta

from fastapi import HTTPException, status
from sqlmodel import Session, or_, select

from app.core import config
from app.core.clock import utc_now
from app.features.f1_accounts.models import User, UserSession
from app.features.f1_accounts.schemas import MIN_PASSWORD_LENGTH, REGISTRATION_ROLES, ROLES

USERNAME_PATTERN = re.compile(r"^[a-z0-9._-]{3,30}$")


# ---------- users ----------

def get_user(db: Session, user_id: int) -> User:
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Account not found.")
    return user


def find_by_username(db: Session, username: str) -> User | None:
    return db.exec(select(User).where(User.username == username)).first()


def register(db: Session, name: str, email: str, username: str, password: str, role: str) -> User:
    """FR-1.4: create a PENDING account that an administrator must approve."""
    username = username.strip().lower()
    email = email.strip().lower()
    if role not in REGISTRATION_ROLES:  # BR-9
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Choose Crew member or Sponsor / Management.")
    if not name.strip():
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Enter your full name.")
    if not USERNAME_PATTERN.match(username):
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            "Usernames use 3-30 letters, numbers, dots, dashes or underscores.",
        )
    if len(password) < MIN_PASSWORD_LENGTH:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, f"Passwords need at least {MIN_PASSWORD_LENGTH} characters."
        )
    if find_by_username(db, username):
        raise HTTPException(status.HTTP_409_CONFLICT, "That username is already taken. Please choose another one.")
    if db.exec(select(User).where(User.email == email)).first():
        raise HTTPException(status.HTTP_409_CONFLICT, "An account with this email address already exists.")

    user = User(name=name.strip(), email=email, username=username, password=password, role=role, status="PENDING")
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate(db: Session, username: str, password: str) -> User:
    """FR-1.1 + BR-8: check the password, then that the account may sign in."""
    user = find_by_username(db, username.strip().lower())
    if user is None or user.password != password:
        # generic message - do not reveal which field was wrong
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Incorrect username or password.")
    messages = {
        "PENDING": "Your account is waiting for an administrator to approve it.",
        "REJECTED": "Your account request was not approved. Please contact the administrator.",
        "SUSPENDED": "Your account is suspended. Please contact the administrator.",
    }
    if user.status in messages:
        raise HTTPException(status.HTTP_403_FORBIDDEN, messages[user.status])
    return user


def change_password(db: Session, user_id: int, current_password: str, new_password: str) -> None:
    user = get_user(db, user_id)
    if user.password != current_password:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Your current password is not correct.")
    if len(new_password) < MIN_PASSWORD_LENGTH:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, f"The new password needs at least {MIN_PASSWORD_LENGTH} characters."
        )
    user.password = new_password
    db.add(user)
    db.commit()


# ---------- sessions (FR-1.2, FR-1.3) ----------

def _key(session_id: str) -> str:
    # the table keeps only a hash of the cookie value, so a copy of the
    # sessions table cannot be used to sign in as someone else
    return hashlib.sha256(session_id.encode()).hexdigest()


def create_session(db: Session, user_id: int) -> str:
    session_id = secrets.token_urlsafe(32)  # random, unguessable
    db.add(
        UserSession(
            id=_key(session_id),
            user_id=user_id,
            expires_at=utc_now() + timedelta(days=config.SESSION_TTL_DAYS),
        )
    )
    db.commit()
    return session_id


def user_for_session(db: Session, session_id: str) -> User | None:
    """Return the ACTIVE user of a valid session and slide its expiry, else None."""
    row = db.get(UserSession, _key(session_id))
    if row is None:
        return None
    user = row.user
    if row.expires_at < utc_now() or user.status != "ACTIVE":
        db.delete(row)
        db.commit()
        return None
    row.expires_at = utc_now() + timedelta(days=config.SESSION_TTL_DAYS)  # FR-1.3 sliding expiry
    db.add(row)
    db.commit()
    db.refresh(user)
    return user


def end_session(db: Session, session_id: str) -> None:
    row = db.get(UserSession, _key(session_id))
    if row is not None:
        db.delete(row)
        db.commit()


def end_all_sessions(db: Session, user_id: int) -> None:
    for row in db.exec(select(UserSession).where(UserSession.user_id == user_id)).all():
        db.delete(row)


# ---------- admin (FR-1.6, FR-1.7) ----------

def list_requests(db: Session) -> list[User]:
    statement = select(User).where(User.status == "PENDING").order_by(User.created_at.desc())  # newest first
    return list(db.exec(statement).all())


def _pending(db: Session, user_id: int) -> User:
    user = get_user(db, user_id)
    if user.status != "PENDING":
        raise HTTPException(status.HTTP_409_CONFLICT, "This request has already been handled.")
    return user


def _save(db: Session, user: User) -> User:
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def approve(db: Session, user_id: int, role: str) -> User:
    user = _pending(db, user_id)
    if role not in ROLES:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Choose a valid role.")
    user.role = role
    user.status = "ACTIVE"
    return _save(db, user)


def reject(db: Session, user_id: int) -> User:
    user = _pending(db, user_id)
    user.status = "REJECTED"
    return _save(db, user)


def list_users(db: Session, search: str = "") -> list[User]:
    """Everyone except PENDING requests (those are on the Requests screen)."""
    statement = select(User).where(User.status != "PENDING")
    term = search.strip().lower()
    if term:
        pattern = f"%{term}%"
        statement = statement.where(
            or_(User.name.ilike(pattern), User.username.ilike(pattern), User.email.ilike(pattern))
        )
    return list(db.exec(statement.order_by(User.name)).all())


def suspend(db: Session, user_id: int, admin_id: int) -> User:
    user = get_user(db, user_id)
    if user_id == admin_id:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "You cannot suspend your own account.")
    if user.status != "ACTIVE":
        raise HTTPException(status.HTTP_409_CONFLICT, "Only active accounts can be suspended.")
    user.status = "SUSPENDED"
    end_all_sessions(db, user_id)  # BR-7: signs the person out everywhere (same commit)
    return _save(db, user)


def reactivate(db: Session, user_id: int) -> User:
    user = get_user(db, user_id)
    if user.status != "SUSPENDED":
        raise HTTPException(status.HTTP_409_CONFLICT, "Only suspended accounts can be reactivated.")
    user.status = "ACTIVE"
    return _save(db, user)
