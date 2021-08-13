# Copyright (C) 2021-2030 StockRead Inc.
# Author: Thanh Tung Nguyen
# Contact: tungstudies@gmail.com

import datetime
import json
import os
import re
from time import sleep

from wsimple import InvalidAccessTokenError, InvalidRefreshTokenError, Wsimple

from src.config.config import BASE_DIR
from src.secrets.credentials import WSIMPLE_USERNAME, WSIMPLE_PASSWORD
from src.utility.emailing import MailBox
from src.utility.singleton import SingletonMeta


# DIVIDER: --------------------------------------
# INFO: WSimpleOTPVerifier Concrete Class

class WSimpleOTPVerifier:

    wsimple = 'support@wealthsimple.com'
    subject = 'Wealthsimple verification code'

    def __init__(self, mailbox: MailBox = MailBox(), otp_wait_time: int = 15):
        self._mailbox = mailbox
        self._otp_wait_time = otp_wait_time

    @property
    def otp(self):
        sleep(self._otp_wait_time)

        email_data = self._mailbox.read_latest(from_sender=self.wsimple, subject_title=self.subject, is_unread=False)

        pattern = re.compile(r'Wealthsimple:<br><br>\r\n\r\n(.*?)\r\n\r\nThis code will')

        otp_key = pattern.findall(email_data['payload'])[0]
        censored_otp = str(otp_key).replace(str(otp_key)[1:-1], '*' * len(str(otp_key)[1:-1]))

        print("OTP collected from email: {}".format(censored_otp))

        return int(otp_key)


# DIVIDER: --------------------------------------
# INFO: WSimpleConnection Concrete Class

class WSimpleConnection(metaclass=SingletonMeta):
    token_refresh_url = "https://trade-service.wealthsimple.com/auth/refresh"

    def __init__(self, token_filepath=os.path.join(BASE_DIR, 'secrets', 'wstokens.json'),
                 username: str = WSIMPLE_USERNAME, password: str = WSIMPLE_PASSWORD,
                 wsimple_verifier: WSimpleOTPVerifier = WSimpleOTPVerifier(), tk_refresh_buffer: int = 600):
        """
        :param tk_refresh_buffer: buffer time (in seconds) to refresh tokens before they expire
        :type tk_refresh_buffer: int
        """
        self._token_filepath = token_filepath
        self._tk_refresh_buffer = tk_refresh_buffer

        self._username = username
        self._password = password
        self._wsimple_verifier = wsimple_verifier
        self._wst_auth = None

        # ALERT: The 6 lines of code below (including the comment) should not be changed in order
        self._expiry_timestamp = 0
        self._access_token = None
        self._refresh_token = None
        self._wsimple_token_dict = self._get_token_info()
        # IMPORTANT: Setup expiry_timestamp, access_token, refresh_token by running the method right below
        self._parse_and_save_tokens()

    def __str__(self):
        tojoin = list()
        tojoin.append('ClassType: {}'.format(type(self).__name__))
        tojoin.append('AccessExpiryTimestamp: {}'.format(self._expiry_timestamp))
        tojoin.append('IsAccessExpiryExpired: {}'.format(self.is_access_expired))
        tojoin.append('TokenRefreshBufferTine: {}'.format(self._tk_refresh_buffer))

        censored_refresh_token = str(self._refresh_token).replace(str(self._refresh_token)[4:-4],
                                                                  '*' * len(str(self._refresh_token)[4:-4]))
        censored_access_token = str(self._access_token).replace(str(self._access_token)[4:-4],
                                                                '*' * len(str(self._access_token)[4:-4]))

        tojoin.append('RefreshToken: {}'.format(censored_refresh_token))
        tojoin.append('AccessToken: {}'.format(censored_access_token))

        censored_username = str(self._username).replace(str(self._username)[3:-3],
                                                        '*' * len(str(self._username)[3:-3]))
        censored_pass = str(self._password).replace(str(self._password)[:],
                                                    '*' * len(str(self._password)[:]))
        tojoin.append('Username: {}'.format(censored_username))
        tojoin.append('Pass: {}'.format(censored_pass))
        tojoin.append('WealthSimpleAuthentication: {}'.format(self.auth))

        tojoin.append('TokenFilepath: {}'.format(self._token_filepath))

        return ', '.join(tojoin)

    # DIVIDER: Publicly Accessible Method Properties ----------------------------------------------
    @property
    def is_access_expired(self):
        return self._expiry_timestamp <= datetime.datetime.now().timestamp().__round__()

    @property
    def auth(self) -> Wsimple:
        if self.is_access_expired:
            print('WealthSimple access has expired. The system is logging in WST to verify')
            return self._login_and_verify()

        else:
            if datetime.datetime.now().timestamp().__round__() > (self._expiry_timestamp - self._tk_refresh_buffer):
                print('WealthSimple access is about to expire. Refreshing the access.')
                return self._refresh_token()

            elif not self._wst_auth:
                self._wst_auth = Wsimple(
                    self._username,
                    self._password,
                    oauth_mode=True,
                    tokens=self._wsimple_token(),
                    internally_manage_tokens=True
                )
                print('Reloading WealthSimple access')
                return self._wst_auth

            else:
                return self._wst_auth

    # DIVIDER: Class Private Methods to Process Data Internally -----------------------------------
    def _get_token_info(self):
        try:
            with open(self._token_filepath) as f:
                return json.load(f)
        except FileNotFoundError as err:
            print(err)

    def _parse_and_save_tokens(self):
        self._expiry_timestamp = self._wsimple_token_dict['expiry_timestamp']
        self._access_token = None if self.is_access_expired else self._wsimple_token_dict['access_token']
        self._refresh_token = None if self.is_access_expired else self._wsimple_token_dict['refresh_token']

        with open(self._token_filepath, 'w') as outfile:
            json.dump(self._wsimple_token_dict, outfile, indent=4, sort_keys=True)

    def _wsimple_token(self):
        if self._access_token and self._refresh_token:
            return [{'Authorization': self._access_token}, {"refresh_token": self._refresh_token}]

    def _login_and_verify(self):
        self._wst_auth = Wsimple(self._username, self._password)
        self._wsimple_token_dict = self._wst_auth.inject_otp(int(self._wsimple_verifier.otp))
        self._parse_and_save_tokens()

        return self._wst_auth

    def _refresh_tokens(self):

        self._wst_auth = Wsimple(
            self._username,
            self._password,
            oauth_mode=True,
            tokens=self._wsimple_token(),
            internally_manage_tokens=True
        )

        try:
            self._wsimple_token_dict = self._wst_auth.refresh_token(self._wsimple_token())
            self._parse_and_save_tokens()
            return self._wst_auth

        except (InvalidAccessTokenError, InvalidRefreshTokenError) as err:
            print("Invalid Token: {}".format(err))
            return self._login_and_verify()


# DIVIDER: --------------------------------------
# INFO: Usage Examples

if __name__ == '__main__':

    is_to_run_test = True

    if is_to_run_test:
        wsimple_conn = WSimpleConnection()
        ws_access = wsimple_conn.auth
        print(ws_access.exchanges)

    else:
        pass
