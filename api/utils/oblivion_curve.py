from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from dateutil.relativedelta import relativedelta


def get_next_answer_date_delta_seconds(
    months: int | None = None, days: int | None = None, hours: int | None = None
):
    now = datetime.now(ZoneInfo('Asia/Tokyo'))
    next_answer_date_delta = relativedelta(
        months=months, days=days, hours=hours
    )
    next_answer_date = now + next_answer_date_delta
    next_answer_date_delta = next_answer_date - now
    next_answer_date_delta_seconds = next_answer_date_delta.total_seconds()
    return next_answer_date_delta_seconds


def get_next_answer_date(next_answer_date_delta_seconds: int):
    now = datetime.now(ZoneInfo('Asia/Tokyo'))
    return now + timedelta(seconds=next_answer_date_delta_seconds)
