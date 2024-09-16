from datetime import datetime, timedelta

from dateutil.relativedelta import relativedelta


def get_next_answer_date_delta_minutes(
    months: int | None = None, days: int | None = None, hours: int | None = None
):
    today = datetime.today()
    next_answer_date_delta = relativedelta(
        months=months, days=days, hours=hours
    )
    next_answer_date = today + next_answer_date_delta
    next_answer_date_delta = next_answer_date - today
    next_answer_date_delta_minutes = next_answer_date_delta.total_seconds()
    return next_answer_date_delta_minutes


def get_next_answer_date(next_answer_date_delta_minutes: int):
    today = datetime.today()
    return today + timedelta(minutes=next_answer_date_delta_minutes)
