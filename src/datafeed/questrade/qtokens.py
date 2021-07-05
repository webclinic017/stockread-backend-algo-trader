import json
import os

import requests
from threading import Lock
from datetime import datetime

from src.config.config import BASE_DIR
from src.secrets import QUESTRADE_TOKENS, QUESTRADE_TOKEN_URL


class SingletonMeta(type):
    """
    This is a thread-safe implementation of Singleton.
    """

    _instances = {}

    _lock: Lock = Lock()
    """
    We now have a lock object that will be used to synchronize threads during
    first access to the Singleton.
    """

    def __call__(cls, *args, **kwargs):
        """
        Possible changes to the value of the `__init__` argument do not affect
        the returned instance.
        """

        with cls._lock:
            if cls not in cls._instances:
                instance = super().__call__(*args, **kwargs)
                cls._instances[cls] = instance
        return cls._instances[cls]


class QuestradeBearerToken(metaclass=SingletonMeta):

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
    qbt = QuestradeBearerToken()
    print(qbt.access_token)
