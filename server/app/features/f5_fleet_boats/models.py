"""Feature 5 - SQLModel table: DM-2 boats.

Written by the project lead in the shared schema PR (team decision D11) -
owner please review. Feature 2 links every record to a boat
(records.boat_id -> boats.id).

Deactivating a boat (active = False) must not break records already linked
to it (BR-6), so boats are never deleted.
"""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime
from sqlmodel import Field, Relationship, SQLModel

from app.core.clock import utc_now

if TYPE_CHECKING:
    from app.features.f2_record_collection.models import Record


class Boat(SQLModel, table=True):
    __tablename__ = "boats"

    id: int | None = Field(default=None, primary_key=True)
    code: str = Field(max_length=20, unique=True, index=True)  # e.g. "HC-14"
    name: str = Field(max_length=120)  # e.g. "Harbor Cleaner"
    capacity_kg: float  # required and > 0 (DM-2) - check it in the service
    active: bool = Field(default=True, index=True)  # True = crews can choose it
    created_at: datetime = Field(default_factory=utc_now, sa_type=DateTime(timezone=True))

    # one boat -> many records
    records: list["Record"] = Relationship(back_populates="boat")
