import uuid
import datetime, time
import pytz
from django.conf import settings

LOCAL_TZ = pytz.timezone(settings.TIME_ZONE)

GREGORIAN_DELTA = 0x01b21dd213814000L

def uuid1_to_datetime(u):
    """
    converts uuid timestamp to naive datetime (UTC)
    """
    ts = (u.time - GREGORIAN_DELTA)

    us = (ts % 10000000) / 10
    ts = ts / 10000000

    return datetime.datetime.utcfromtimestamp(ts).replace(microsecond=us)

def datetime_to_uuid1(dt, clock_seq=0, node=None):
    """
    converts datetime to uuid1 (treated as UTC if naive, tzinfo also is supported)
    node is 48-bit int, default 0
    clock_seq - 14-bit int, default 0
    """
    if not dt.tzinfo:
        dt = pytz.utc.localize(dt)
    dt = dt.astimezone(LOCAL_TZ).replace(tzinfo=None)

    t = GREGORIAN_DELTA + long(time.mktime(dt.timetuple())) * 10000000
    t += dt.microsecond * 10
    clock_seq_low = clock_seq & 0xffL
    clock_seq_hi_variant = (clock_seq >> 8L) & 0x3fL
    if node is None:
        node = uuid.getnode()
    fields = (t & 0xffffffff, (t >> 32) & 0xffff, t >> 48, 
                clock_seq_hi_variant, clock_seq_low, node)
    return uuid.UUID(fields=fields, version=1)

