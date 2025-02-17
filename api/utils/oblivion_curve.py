from datetime import datetime, timedelta
from zoneinfo import ZoneInfo


MONTH = 2592000
DAY = 86400
HOUR = 3600

level_and_score_mapping = {
    1: 'level_one',
    2: 'level_two',
    3: 'level_three',
    4: 'level_four',
    5: 'level_five',
    6: 'level_six',
    7: 'level_seven',
}


def get_next_answer_date_delta_seconds(
    months: int | None = None, days: int | None = None, hours: int | None = None
):
    return months * MONTH + days * DAY + hours * HOUR


def get_next_answer_date(next_answer_date_delta_seconds: int):
    now = datetime.now(ZoneInfo('Asia/Tokyo'))
    return now + timedelta(seconds=next_answer_date_delta_seconds)
