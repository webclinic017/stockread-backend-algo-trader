import json
import os
import re
from datetime import datetime
from threading import Lock
from time import sleep
from typing import Optional, List

import requests
from wsimple import InvalidAccessTokenError, InvalidRefreshTokenError, Wsimple

from src.config.config import BASE_DIR
from src.secrets import WSIMPLE_EMAIL, WSIMPLE_PASSWORD, WSIMPLE_TOKENS
from src.utility.emailing import MailBox


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


class ConnectionWST(metaclass=SingletonMeta):
    def __init__(self):
        self.expiry_timestamp = int(WSIMPLE_TOKENS['expiry_timestamp']) if WSIMPLE_TOKENS else 0
        self.ws_tokens: Optional[List[dict]] = [{'Authorization': WSIMPLE_TOKENS['access_token']},
                                                {"refresh_token": WSIMPLE_TOKENS[
                                                    'refresh_token']}] if WSIMPLE_TOKENS else None

        self.ws_access: Optional[Wsimple] = None
        self.is_connected: bool = False

    def connect(self):
        if self.check_expired():
            # login to Wealthsimple
            self._login()
            token_resp = self._verify_access()
            self.is_connected = True if token_resp else False
            self.expiry_timestamp = token_resp['expiry_timestamp'] if token_resp else 0
            self.ws_tokens = [{'Authorization': token_resp['access_token']},
                              {"refresh_token": token_resp['refresh_token']}] if token_resp else None

        else:
            try:
                self.ws_access = Wsimple(
                    WSIMPLE_EMAIL,
                    WSIMPLE_PASSWORD,
                    oauth_mode=True,
                    tokens=self.ws_tokens,
                    internally_manage_tokens=True
                )
                self.ws_access.refresh_token(self.ws_tokens)
                self.is_connected = True

            except (InvalidAccessTokenError, InvalidRefreshTokenError) as err:
                print("Invalid Token: {}".format(err))

    def _login(self, username=WSIMPLE_EMAIL, password=WSIMPLE_PASSWORD):
        self.ws_access = Wsimple(username, password)

    def _verify_access(self):
        sleep(10)
        mailbox = MailBox()
        _, data = mailbox.read_latest(from_sender='support@wealthsimple.com',
                                      subject_title='Wealthsimple verification code', is_unread=False)

        pattern = re.compile(r'Wealthsimple:<br><br>\r\n\r\n(.*?)\r\n\r\nThis code will')
        otp_key = pattern.findall(data['payload'])[0]
        print("OTP collected from email: {}".format(otp_key))
        ws_tokens = self.ws_access.inject_otp(int(otp_key))
        with open(os.path.join(BASE_DIR, 'secrets/wstokens.json'), 'w') as f:
            json.dump(ws_tokens, f)

        return ws_tokens

    def _refresh_token(self):
        r = requests.post(
            url="https://trade-service.wealthsimple.com/auth/refresh",
            data=self.ws_tokens[1],
        )
        if r.status_code == 401:
            raise InvalidRefreshTokenError
        else:
            token_dict = {'access_token': r.headers["X-Access-Token"],
                          'refresh_token': r.headers["X-Refresh-Token"],
                          'expiry_timestamp': int(r.headers["X-Access-Token-Expires"])}

            with open(os.path.join(BASE_DIR, 'secrets/wstokens.json'), 'w') as f:
                json.dump(token_dict, f)

            self.ws_tokens = [{'Authorization': r.headers['X-Access-Token']},
                              {"refresh_token": r.headers['X-Refresh-Token']}]

            self.expiry_timestamp = int(r.headers["X-Access-Token-Expires"])

    def check_expired(self):
        if self.is_connected:
            if datetime.now().timestamp().__round__() - (self.expiry_timestamp - 10 * 60) > 0:
                self._refresh_token()
                self.connect()

        else:
            return datetime.now().timestamp().__round__() > self.expiry_timestamp


if __name__ == '__main__':
    conn_wst = ConnectionWST()
    conn_wst.connect()
    ws_access = conn_wst.ws_access

