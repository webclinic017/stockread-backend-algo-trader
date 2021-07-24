import requests

from src.datafeed.questrade.qtokens import QuesTradeBearerToken


class QuesTradeApi:
    def __init__(self, ticker_symbol: str, qt_token=QuesTradeBearerToken()):
        self.qt_token = qt_token
        self.ticker_symbol = ticker_symbol
        self.headers = {
            'Authorization': 'Bearer {}'.format(self.qt_token.access_token)
        }
        self.symbol_id = self.get_symbol_id()

    def get_symbol_id(self):
        ticker_search_suffix = 'v1/symbols/search?prefix'
        url = f"{self.qt_token.api_server}{ticker_search_suffix}={self.ticker_symbol}"

        request_attempts = 3
        data = None
        for _ in range(request_attempts):
            response = requests.request("GET", url, headers=self.headers)
            data = response.json()
            if data['symbols']:
                break

        try:
            symbols_found = data['symbols']
            for each in symbols_found:
                if each['symbol'] == self.ticker_symbol:
                    return each['symbolId']

        except KeyError as err:
            print(err)

    def get_quotes(self):
        market_quotes_suffix = 'v1/markets/quotes/'

        url = f"{self.qt_token.api_server}{market_quotes_suffix}{self.symbol_id}"

        response = requests.request("GET", url, headers=self.headers)
        data = response.json()
        result = data['quotes'][0]
        return result


if __name__ == '__main__':
    pass
