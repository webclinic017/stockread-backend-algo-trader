"""
Function to check if today's date is a weekend day (i.e. Saturday or Sunday)
"""
import datetime


def check_if_weekend(today):
    try:
        isinstance(today, datetime.datetime)
        upper_limit = today + datetime.timedelta(days=(6 - today.weekday()))
        lower_limit = today + datetime.timedelta(days=(5 - today.weekday()))
        if today >= lower_limit <= upper_limit:
            print('It is the weekend!')
        else:
            print('It is not the weekend!')
    except ValueError:
        print('Your date is not a datetime object.')


if __name__ == "__main__":
    today_date = datetime.datetime.today()
    check_if_weekend(today_date)
