from typing import Union, Optional, Dict
import dateparser
import pytz
from tzlocal import get_localzone
from datetime import datetime


# get local timezone    
local_tz = get_localzone() 


def date_to_milliseconds(date_str: Union[str, datetime]) -> int:
    """
    Adapted from binance module: An unofficial Python wrapper for the Binance exchange API v3
    
    Convert UTC date to milliseconds

    If using offset strings add "UTC" to date string e.g. "now UTC", "11 hours ago UTC"

    See dateparse docs for formats http://dateparser.readthedocs.io/en/latest/

    :param date_str: date in readable format, i.e. "January 01, 2018", "11 hours ago UTC", "now UTC"
    """
    # get epoch value in UTC
    epoch: datetime = datetime.utcfromtimestamp(0).replace(tzinfo=pytz.utc)
    # parse our date string
    if type(date_str)==datetime:
        d = date_str
    else:
        d: Optional[datetime] = dateparser.parse(date_str)
    # if the date is not timezone aware apply UTC timezone
    if d.tzinfo is None or d.tzinfo.utcoffset(d) is None:
        d = d.replace(tzinfo=local_tz)

    # return the difference in time
    return int((d - epoch).total_seconds() * 1000.0)


def milliseconds_to_date(int_date: int) -> datetime:
    return datetime.fromtimestamp(int_date/1000)


if __name__=="__main__":
    original_date = "January 02, 2021"
    dt_int = date_to_milliseconds(original_date)
    dt_stamp = datetime.fromtimestamp(dt_int/1000)
    milliseconds_to_date(dt_int)

    print(f'{original_date} / {dt_stamp} / {dt_int}')
