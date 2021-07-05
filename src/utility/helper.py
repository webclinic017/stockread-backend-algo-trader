import datetime
from typing import List, IO, Union
from dateutil import parser


def zdatetime_to_timestamp(zdatetime_str: str) -> int:
    datetime_obj = datetime.datetime.strptime(zdatetime_str, '%Y-%m-%dT%H:%M:%SZ')
    return int(datetime_obj.timestamp())


def timestamp_to_zdatetime(timestamp: int) -> str:
    datetime_obj = datetime.datetime.fromtimestamp(timestamp)
    return datetime_obj.strftime('%Y-%m-%dT%H:%M:%SZ')


def zdatetime_to_object(zdatetime_str: str) -> datetime.datetime:
    return datetime.datetime.strptime(zdatetime_str, '%Y-%m-%dT%H:%M:%SZ')


def object_to_zdatetime(datetime_obj: datetime.datetime) -> str:
    return datetime_obj.strftime('%Y-%m-%dT%H:%M:%SZ')


def get_backdate_timestamp(minutes=0, hours=0, days=0):
    time_amount_in_minutes = minutes + (hours + 24 * days) * 60
    current_date = datetime.datetime.now().replace(microsecond=0)
    new_date = current_date - datetime.timedelta(minutes=time_amount_in_minutes)
    return new_date.timestamp()


def time_ago(usertime: Union[bytes, str, int, IO[str], IO]):
    """
    Get a datetime object or a int() Epoch timestamp and return a
    pretty string like 'an hour ago', 'yesterday', '3 months ago',
    'just now', etc
    Modified from: http://stackoverflow.com/a/1551394/141084
    """
    now = datetime.datetime.utcnow()
    if type(usertime) is int:
        diff = now - datetime.datetime.fromtimestamp(usertime)

    elif type(usertime) is str:
        converted_time = parser.parse(usertime).replace(tzinfo=None)
        diff = now - converted_time

    elif isinstance(usertime, datetime.datetime):
        diff = now - usertime
    elif not usertime:
        diff = now - now
    else:
        raise ValueError('invalid date %s of type %s' % (usertime, type(usertime)))
    second_diff = diff.seconds
    day_diff = diff.days

    if day_diff < 0:
        return ''

    if day_diff == 0:
        if second_diff < 10:
            return "just now"
        if second_diff < 60:
            return str(second_diff) + " seconds ago"
        if second_diff < 120:
            return "a minute ago"
        if second_diff < 3600:
            return str(int(second_diff / 60)) + " minutes ago"
        if second_diff < 7200:
            return "an hour ago"
        if second_diff < 86400:
            return str(int(second_diff / 3600)) + " hours ago"
    if day_diff == 1:
        return "yesterday"
    if day_diff < 7:
        return str(day_diff) + " days ago"
    if day_diff < 31:
        return str(day_diff / 7) + " weeks ago"
    if day_diff < 365:
        return str(day_diff / 30) + " months ago"
    return str(day_diff / 365) + " years ago"


def kmb_to_number(str_num: str) -> int:
    """
    :param str_num: representational string of a number (i.e.: 10K, 9.3M, 1.25B)
    :type str_num: str
    :return: integer number of the given string
    :rtype: int
    """
    int_num = 0
    num_map = {'K': 1000, 'M': 1000000, 'B': 1000000000}
    if str_num.isdigit():
        int_num = int(str_num)
    else:
        if len(str_num) > 1 and str_num[:-1].isnumeric():
            int_num = float(str_num[:-1]) * num_map.get(str_num[-1].upper(), 1)
    return int(int_num)


def listdict_to_dictdict(dict_list: List[dict], value_to_key: str) -> dict:
    """
    :param dict_list: the input list of dictionaries
    :type dict_list: List[dict]
    :param value_to_key: one of the keys of each inner dictionary whose value is to be converted to keys of topmost dict
    :type value_to_key: str
    :return: the input dict of dictionaries
    :rtype: dict
    """
    # short form
    # return {item_dict.pop(value_to_key): item_dict for item_dict in dict_list}

    dict_dict = dict()
    for item_dict in dict_list:
        popped_key = item_dict.pop(value_to_key)
        popped_value = item_dict
        dict_dict[popped_key] = popped_value
    return dict_dict


if __name__ == '__main__':
    pass
