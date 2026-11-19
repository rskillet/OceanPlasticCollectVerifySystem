"""Shared schema and seed checks (SHARED FILE) - tables from the schema PR (D11)."""

from sqlmodel import select

from app.core.clock import THAILAND, thailand_day_start, thailand_month_start, utc_now
from app.features.f1_accounts.models import User
from app.features.f2_record_collection.models import Photo, Record, make_record_number
from app.features.f5_fleet_boats.models import Boat
from app.seed import seed_if_empty


def test_seed_creates_demo_data(db):
    assert len(db.exec(select(User)).all()) == 8
    assert [b.code for b in db.exec(select(Boat).order_by(Boat.id)).all()] == ["HC-14", "SH-02", "RM-07", "SL-03"]
    records = db.exec(select(Record)).all()
    assert {r.status for r in records} == {"PENDING", "VERIFIED", "REJECTED"}
    assert all(r.reason for r in records if r.status == "REJECTED")  # BR-4
    assert len(db.exec(select(Photo)).all()) == len(records)  # one photo per record


def test_seed_runs_only_once(db):
    users_before = len(db.exec(select(User)).all())
    assert seed_if_empty() is False  # data exists -> nothing added
    assert len(db.exec(select(User)).all()) == users_before


def test_record_number_and_boat_relationship(db):
    record = db.exec(select(Record).order_by(Record.id)).first()
    assert record.record_number == make_record_number(record.id) == f"REC-{1000 + record.id}"
    assert record.boat.code in {"HC-14", "SH-02", "RM-07", "SL-03"}
    assert record in record.boat.records


def test_thailand_day_and_month_start():
    start = thailand_day_start()
    local = start.astimezone(THAILAND)
    assert (local.hour, local.minute) == (0, 0)
    assert start <= utc_now()
    assert thailand_month_start().astimezone(THAILAND).day == 1


def test_records_today_in_thailand(db):
    today = db.exec(select(Record).where(Record.recorded_at >= thailand_day_start())).all()
    assert len(today) >= 2  # two pending records for Marco today
