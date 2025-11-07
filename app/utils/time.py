import os
from datetime import datetime, date, time as dtime
import zoneinfo
from dateutil import parser as dtparser

def _tz():
    return zoneinfo.ZoneInfo(os.getenv("TZ", "America/Mexico_City"))

CDMX_TZ = _tz()
UTC_TZ = zoneinfo.ZoneInfo("UTC")

def now_cdmx() -> datetime:
    return datetime.now(tz=CDMX_TZ)

def to_cdmx(dt: datetime) -> datetime:
    return dt.astimezone(CDMX_TZ) if dt.tzinfo else dt.replace(tzinfo=CDMX_TZ)

def to_utc(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=CDMX_TZ)
    return dt.astimezone(UTC_TZ)

def parse_date_or_datetime_to_utc(value: str, *, as_start=False, as_end=False) -> datetime:
    v = value.strip()
    if len(v) == 10 and v[4] == "-" and v[7] == "-":
        d = date.fromisoformat(v)
        t = dtime(23, 59, 59, 999999) if as_end else dtime(0, 0, 0, 0)
        dt = datetime.combine(d, t, tzinfo=CDMX_TZ)
        return to_utc(dt)
    dt = dtparser.isoparse(v)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=CDMX_TZ)
    return to_utc(dt)
