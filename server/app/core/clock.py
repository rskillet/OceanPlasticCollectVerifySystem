"""Date and time helpers (SHARED FILE).

Team decision (docs/DECISIONS.md D10): the operator works in Thailand, so
"today", "this month" and "this year" mean Thailand time (UTC+7, no daylight
saving). The database always stores UTC; convert only when you group by day,
month or year, or when you need the local date.

    from app.core.clock import utc_now, thailand_month_start

    start = thailand_month_start()          # UTC datetime of 1st of this month, 00:00 Thailand
    select(Record).where(Record.recorded_at >= start)
"""

from datetime import datetime, timedelta, timezone

# Asia/Bangkok is always UTC+7. A fixed offset needs no extra time zone package.
THAILAND = timezone(timedelta(hours=7), "Asia/Bangkok")


def utc_now() -> datetime:
    """Current time in UTC (timezone-aware). Use this for every created_at."""
    return datetime.now(timezone.utc)


def to_thailand(value: datetime) -> datetime:
    """Show a stored UTC time in Thailand time."""
    if value.tzinfo is None:  # treat naive values as UTC
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(THAILAND)


def thailand_day_start(now: datetime | None = None) -> datetime:
    """Start of today in Thailand, returned in UTC for database queries."""
    local = to_thailand(now or utc_now())
    return local.replace(hour=0, minute=0, second=0, microsecond=0).astimezone(timezone.utc)


def thailand_month_start(now: datetime | None = None) -> datetime:
    """1st day of this month, 00:00 Thailand time, returned in UTC."""
    local = to_thailand(now or utc_now())
    return local.replace(day=1, hour=0, minute=0, second=0, microsecond=0).astimezone(timezone.utc)


def thailand_year_start(now: datetime | None = None) -> datetime:
    """1 January this year, 00:00 Thailand time, returned in UTC."""
    local = to_thailand(now or utc_now())
    return local.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0).astimezone(timezone.utc)
