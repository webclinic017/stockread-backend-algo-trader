from typing import Optional

import requests

from feed.questrade.qtokens import QuestradeBearerToken


class QuestradeApi:
    def __init__(self, questrade_token: Optional[QuestradeBearerToken], ticker_symbol: str):
        self.questrade_token = questrade_token
        self.ticker_symbol = ticker_symbol
        self.headers = {
            'Authorization': 'Bearer {}'.format(self.questrade_token.access_token)
        }
        self.symbol_id = self.get_symbol_id()

    def get_symbol_id(self):
        TICKER_SEARCH_SUFFIX = 'v1/symbols/search?prefix'

        url = f"{self.questrade_token.api_server}{TICKER_SEARCH_SUFFIX}={self.ticker_symbol}"

        response = requests.request("GET", url, headers=self.headers)
        data = response.json()
        for each in data['symbols']:
            if each['symbol'] == self.ticker_symbol:
                return each['symbolId']

    def get_quotes(self):
        MARKET_QUOTES_SUFFIX = 'v1/markets/quotes/'

        url = f"{self.questrade_token.api_server}{MARKET_QUOTES_SUFFIX}{self.symbol_id}"

        response = requests.request("GET", url, headers=self.headers)
        data = response.json()
        result = data['quotes'][0]
        return result


if __name__ == '__main__':
    qbt = QuestradeBearerToken()
    qapi = QuestradeApi(qbt, 'SHOP.TO')
    print(qapi.get_quotes())
    # print(qapi.get_quotes())
