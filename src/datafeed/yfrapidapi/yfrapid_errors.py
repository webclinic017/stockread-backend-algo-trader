class YahooFinanceRangeSettingdError(Exception):
    """Error thrown when a data range is set conflict with the chosen range setting"""

    def __init__(self):
        super(YahooFinanceRangeSettingdError, self).__init__("The chosen range setting conflicts with the range inputs")


class YahooFinanceInvalidIntervalError(Exception):
    """Error thrown when a interval input is not one of 1m|2m|5m|15m allowed options"""

    def __init__(self):
        super(YahooFinanceInvalidIntervalError, self).__init__("The interval input parameter is invalid")


class NotRegularHoursDataRequest(Exception):
    """Error thrown when a data request by minute/minutes is not within regular trading hours"""

    def __init__(self):
        super(NotRegularHoursDataRequest, self).__init__("The by-minute data request  is not in regular trading hours")
