# Copyright (C) 2021-2030 StockRead Inc.
# Author: Thanh Tung Nguyen
# Contact: tungstudies@gmail.com

import datetime
import json
import os
import time

import requests

from src.config.config import BASE_DIR
from src.utility.singleton import SingletonMeta


# DIVIDER: --------------------------------------
# INFO: QuestradeQuoter Concrete Class

class QuesTradeAPI(metaclass=SingletonMeta):

    host = 'https://login.questrade.com'
    endpoint = '/oauth2/token'
    token_url = f'{host}{endpoint}'.format(host=host, endpoint=endpoint)

    def __init__(self, token_filepath=os.path.join(BASE_DIR, 'secrets', 'qtokens.json')):
        self._token_filepath = token_filepath
        self._questrade_tokens = self._get_token_info()

        self._expiry_timestamp = self._questrade_tokens['expiry_timestamp']
        self._refresh_expiry_timestamp = self._questrade_tokens['refresh_expiry_timestamp']
        self._refresh_token = self._questrade_tokens['refresh_token']

        self._access_token = None if self.is_access_expired else self._questrade_tokens['access_token']
        self._api_server = None if self.is_access_expired else self._questrade_tokens['api_server']

        if self.is_refresh_token_expired:
            self._request_access_token()



        self._data_request_headers = {
            'Authorization': 'Bearer {}'.format(self._access_token)
        }

        self._ticker_id_dict: dict = dict()

    def __str__(self):
        tojoin = list()
        tojoin.append('ClassType: {}'.format(type(self).__name__))
        tojoin.append('AccessExpiryTimestamp: {}'.format(self._expiry_timestamp))
        tojoin.append('RefreshTokenExpiryTimestamp: {}'.format(self._refresh_expiry_timestamp))
        tojoin.append('IsAccessExpiryExpired: {}'.format(self.is_access_expired))
        tojoin.append('IsRefreshTokenExpiryExpired: {}'.format(self.is_refresh_token_expired))
        tojoin.append('ApiServer: {}'.format(self._api_server))
        censored_refresh_token = str(self._refresh_token).replace(str(self._refresh_token)[4:-4],
                                                                  '*' * len(str(self._refresh_token)[4:-4]))
        censored_access_token = str(self._access_token).replace(str(self._access_token)[4:-4],
                                                                '*' * len(str(self._access_token)[4:-4]))
        tojoin.append('RefreshToken: {}'.format(censored_refresh_token))
        tojoin.append('AccessToken: {}'.format(censored_access_token))
        tojoin.append('TokenFilepath: {}'.format(self._token_filepath))

        return ', '.join(tojoin)

    # DIVIDER: Publicly Accessible Method Properties ----------------------------------------------
    @property
    def is_access_expired(self):
        return self._expiry_timestamp <= datetime.datetime.now().timestamp().__round__()

    @property
    def is_refresh_token_expired(self):
        return self._refresh_expiry_timestamp <= datetime.datetime.now().timestamp().__round__()

    # DIVIDER: Publicly Accessible Methods --------------------------------------------------------
    def set_refresh_token(self, new_refresh_token: str):
        self._refresh_token = new_refresh_token
        self._request_access_token()

    def find_ticker_id(self, ticker_symbol: str, request_attempts=5):
        if ticker_symbol in self._ticker_id_dict:
            return self._ticker_id_dict[ticker_symbol]
        else:
            ticker_search_suffix = 'v1/symbols/search?prefix'
            url = f"{self._api_server}{ticker_search_suffix}={ticker_symbol}"
            data = None
            for _ in range(request_attempts):
                time.sleep(0.1)
                response = requests.request("GET", url, headers=self._data_request_headers)
                data = response.json()
                if data['symbols']:
                    break

            try:
                symbols_found = data['symbols']
                for each in symbols_found:
                    if each['symbol'] == ticker_symbol:
                        self._ticker_id_dict[ticker_symbol] = each['symbolId']
                        return each['symbolId']

            except Exception as err:
                raise Exception(f'PotentialKeyError: TickerID corresponding to {ticker_symbol} not found'
                                f' in the response. Error details: {err}')

    def get_quotes(self, ticker_symbol: str):
        market_quotes_suffix = 'v1/markets/quotes/'

        ticker_id = self.find_ticker_id(ticker_symbol=ticker_symbol)
        url = f"{self._api_server}{market_quotes_suffix}{ticker_id}"

        response = requests.request("GET", url, headers=self._data_request_headers)
        json_data = response.json()
        return json_data['quotes'][0]

    # DIVIDER: Class Private Methods to Process Data Internally -----------------------------------
    def _get_token_info(self):
        try:
            with open(self._token_filepath) as f:
                return json.load(f)
        except FileNotFoundError as err:
            print(err)

    def _request_access_token(self):
        if self.is_access_expired:
            if self._refresh_token:
                params = {
                    'grant_type': 'refresh_token',
                    'refresh_token': self._refresh_token
                }

                resp_text = "PotentialBadRequest"
                try:
                    response = requests.post(url=self.token_url, params=params)
                    resp_text = response.text
                    json_response = response.json()
                    print(json_response)
                except Exception as err:
                    raise Exception(f'{resp_text}: the refresh token might have expired. Error details: {err}')

                # refresh token is renewed on each access request
                self._refresh_token = json_response['refresh_token']
                self._refresh_expiry_timestamp = round(datetime.datetime.now().timestamp()) + 603000  # 167.5 hrs ~ 7d
                self._access_token = json_response['access_token']
                self._api_server = json_response['api_server']
                self._expiry_timestamp = round(datetime.datetime.now().timestamp()) + int(json_response['expires_in'])

                json_response['expiry_timestamp'] = self._expiry_timestamp
                json_response['refresh_expiry_timestamp'] = self._refresh_expiry_timestamp

                with open(self._token_filepath, 'w') as outfile:
                    json.dump(json_response, outfile, indent=4, sort_keys=True)

                expiry_time_readable = datetime.datetime.fromtimestamp(self._expiry_timestamp).isoformat()
                print("The new token is retrieved and valid until: {}".format(expiry_time_readable))
            else:
                raise Exception('RefreshTokenExpired: Unable to request access token with EXPIRED refresh token')


# DIVIDER: --------------------------------------
# INFO: Usage Examples

if __name__ == '__main__':
    questrade_api = QuesTradeAPI()
    print(questrade_api)
    quotes = questrade_api.get_quotes('CTS.TO')
    print(quotes)
