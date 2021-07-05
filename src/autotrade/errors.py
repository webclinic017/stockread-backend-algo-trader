class TickerSymbolNotFound(Exception):
    """Error thrown when a ticker search gives no results or unmatched ticker symbols"""

    def __init__(self):
        super(TickerSymbolNotFound, self).__init__("Ticker symbol could not be found")


class NegativeCashBalance(Exception):
    """
    Error thrown when a negative cash amount being added to the current cash balance and resulting to a negative
    cash balance
    """

    def __init__(self):
        super(NegativeCashBalance, self).__init__("A negative cash balance cannot be set")


class InvalidBrokerTradeSetting(Exception):
    """
    Error thrown when a trading mode conflicts with broker class (i.e.: live trading >< back test broker class,
    or backtest >< live trading broker class
    """

    def __init__(self):
        super(InvalidBrokerTradeSetting, self).__init__("Invalid Broker class selected")
