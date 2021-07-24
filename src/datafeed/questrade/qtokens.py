import json
import os
from datetime import datetime

import requests

from src.config.config import BASE_DIR
from src.secrets.credentials import QUESTRADE_TOKENS, QUESTRADE_TOKEN_URL
from src.utility.singleton import SingletonMeta


class QuesTradeBearerToken(metaclass=SingletonMeta):

    def __init__(self):
        self.expiry_timestamp = QUESTRADE_TOKENS['expiry_timestamp']

    def request_access_tokens(self):

        if self.expiry_timestamp > datetime.now().timestamp().__round__():
            return QUESTRADE_TOKENS['access_token'], QUESTRADE_TOKENS['api_server']

        else:
            params = {
                'grant_type': 'refresh_token',
                'refresh_token': QUESTRADE_TOKENS['refresh_token']
            }

            response = requests.post(QUESTRADE_TOKEN_URL, params=params)
            json_response = response.json()
            self.expiry_timestamp = int(datetime.now().timestamp().__round__()) + int(json_response["expires_in"])
            json_response['expiry_timestamp'] = int(datetime.now().timestamp().__round__()) + int(
                json_response["expires_in"])

            with open(os.path.join(BASE_DIR, 'secrets/qtokens.json'), 'w') as f:
                json.dump(json_response, f)

            access_token = json_response["access_token"]
            api_server = json_response["api_server"]

            expiry_time_readable = datetime.fromtimestamp(self.expiry_timestamp).isoformat()
            print("The new token is retrieved and valid until: {}".format(expiry_time_readable))

            return access_token, api_server

    @property
    def access_token(self):
        access_token, _ = self.request_access_tokens()
        return access_token

    @property
    def api_server(self):
        _, api_server = self.request_access_tokens()
        return api_server

    def __str__(self):
        return self.access_token


if __name__ == '__main__':
    qbt = QuesTradeBearerToken()
    print(qbt.access_token)
