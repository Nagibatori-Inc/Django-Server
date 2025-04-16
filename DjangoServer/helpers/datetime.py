import calendar
from datetime import datetime, timedelta


def get_month_length(date: datetime):
    return calendar.monthrange(date.year, date.month)[1]


def renew_for_month(date: datetime):
    return date + timedelta(days=get_month_length(date))
