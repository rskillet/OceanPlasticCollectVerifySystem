"""Feature 2 - SQLModel tables: DM-3 records and photos.

Written by the project lead in the shared schema PR (team decision D11) -
owner please review. Features 3, 4 and 5 read the records table and Feature 4
updates its status, so announce any change in the team chat.

Photos (team decision D9): the image bytes live in their own `photos` table,
one row per record. List queries on `records` never load the image, so the
history, queue and dashboard stay fast. Load a photo only for the photo
endpoint:  session.exec(select(Photo).where(Photo.record_id == record_id)).first()

Records are immutable after saving (BR-3): no update/delete endpoints, except
Feature 4 setting status / reviewed_by / reviewed_at / reason.
"""

from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime
from sqlmodel import Field, Relationship, SQLModel

from app.core.clock import utc_now
from app.features.f5_fleet_boats.models import Boat

MATERIALS = ("PET_BOTTLES", "HDPE_RIGID", "FISHING_NET_ROPE", "LDPE_FILM", "MIXED")
STATUSES = ("PENDING", "VERIFIED", "REJECTED")


def make_record_number(record_id: int) -> str:
    """Record number shown to users (team decision D10): id 43 -> "REC-1043"."""
    return f"REC-{1000 + record_id}"


class Record(SQLModel, table=True):
    __tablename__ = "records"

    id: int | None = Field(default=None, primary_key=True)
    # made by the phone when the crew saves the record; the same client_id sent
    # twice (offline sync retry) must not create a second record (BR-10)
    client_id: str = Field(default_factory=lambda: str(uuid4()), max_length=36, unique=True, index=True)
    # set right after the first flush, when the id is known: make_record_number(id)
    record_number: str | None = Field(default=None, max_length=20, unique=True, index=True)

    boat_id: int = Field(foreign_key="boats.id", index=True)
    crew_id: int = Field(foreign_key="users.id", index=True)  # taken from the session (BR-11)
    weight_kg: float  # > 0, checked in the service
    material: str = Field(max_length=30)  # one of MATERIALS
    note: str | None = Field(default=None, max_length=500)
    latitude: float | None = None
    longitude: float | None = None
    gps_accuracy_m: float | None = None
    recorded_at: datetime = Field(sa_type=DateTime(timezone=True), index=True)  # when the crew weighed it

    status: str = Field(default="PENDING", max_length=20, index=True)  # one of STATUSES
    reviewed_by: int | None = Field(default=None, foreign_key="users.id")  # Feature 4
    reviewed_at: datetime | None = Field(default=None, sa_type=DateTime(timezone=True))
    reason: str | None = Field(default=None, max_length=500)  # required when REJECTED (BR-4)
    created_at: datetime = Field(default_factory=utc_now, sa_type=DateTime(timezone=True))

    # TODO(CHG-003): auto_verified, verified_rule, spot_check columns
    # TODO(CHG-002/CHG-003): reversed_by, reversed_at, reversal_reason (a VERIFIED record can be reversed)
    # TODO(CHG-004): record_flags table (DUPLICATE_PHOTO, OUTSIDE_LANDING_SITE) - see docs/CHANGE_REQUESTS.md

    # many records -> one boat (record.boat.code, record.boat.name)
    boat: Boat = Relationship(back_populates="records")


class Photo(SQLModel, table=True):
    """The scale photo of one record, kept out of the records table for speed."""

    __tablename__ = "photos"

    id: int | None = Field(default=None, primary_key=True)
    # TODO(CHG-004): two photos per record - add `kind` (PLASTIC | SCALE) and `sha256`,
    # and make (record_id, kind) unique instead of record_id alone
    record_id: int = Field(foreign_key="records.id", unique=True, index=True)  # one photo per record
    content_type: str = Field(max_length=50)  # e.g. "image/jpeg"
    size_bytes: int
    data: bytes  # the image itself (BYTEA in PostgreSQL)
    created_at: datetime = Field(default_factory=utc_now, sa_type=DateTime(timezone=True))
