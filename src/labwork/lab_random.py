# import random
#
# for _ in range(100):
#     rand = random.uniform(0, 1)
#     selected_rand = rand if rand < 0.85 else ''
#     print(rand, selected_rand)

# list1 = [1, 2, 3]
# list2 = [4, 5, 6]
# list2.append(list1.pop(1))
# print(list1)
# print(list2)
#
# # sth = 5
# # assert sth in list1
#
def simple_enum(operation_type: str = 'solar'):
    operation_types = {'update', 'insert', 'remove'}

    if operation_type not in operation_types:
        raise ValueError(f"InvalidOperationType: expected one of: {operation_types}")

#
#
# sim_func(1, 2, 3, sim_type='cu')

myorders = {'ord_1': '123', 'ord_2': '456'}
print(myorders.pop('ord_1'))


class Networkerror(RuntimeError):
   def __init__(self, arg):
      self.args = arg


# try:
#    raise Networkerror("Bad hostname")
# except Networkerror,e:
#    print e.args

'''
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




def _verify_access(self):
    pattern = re.compile(r'Wealthsimple:<br><br>\r\n\r\n(.*?)\r\n\r\nThis code will')
    otp_key = pattern.findall(data['payload'])[0]
    print("OTP collected from email: {}".format(otp_key))
    ws_tokens = self.ws_access.inject_otp(int(otp_key))
    ws_tokens = self.wst_auth.inject_otp(int(otp_key))
    with open(os.path.join(BASE_DIR, 'secrets/wstokens.json'), 'w') as f:
        json.dump(ws_tokens, f)

    return ws_tokens

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
                self.wst_auth = Wsimple(
                    WSIMPLE_EMAIL,
                    WSIMPLE_PASSWORD,
                    oauth_mode=True,
                    tokens=self.ws_tokens,
                    internally_manage_tokens=True
                )
                self.ws_access.refresh_token(self.ws_tokens)
                self.wst_auth.refresh_token(self.ws_tokens)
                self.is_connected = True

            except (InvalidAccessTokenError, InvalidRefreshTokenError) as err:
                print("Invalid Token: {}".format(err))

    def _login(self, username=WSIMPLE_EMAIL, password=WSIMPLE_PASSWORD):
        self.ws_access = Wsimple(username, password)


    def _refresh_tokens(self):

        r = requests.post(
            url="https://trade-service.wealthsimple.com/auth/refresh",
            data=self._access_token,
        )
        if r.status_code == 401:
            raise InvalidRefreshTokenError
        else:
            self._wsimple_token_dict = {'access_token': r.headers["X-Access-Token"],
                                        'refresh_token': r.headers["X-Refresh-Token"],
                                        'expiry_timestamp': int(r.headers["X-Access-Token-Expires"])}
            self._parse_and_save_tokens()

            self.ws_tokens = [{'Authorization': r.headers['X-Access-Token']},
                              {"refresh_token": r.headers['X-Refresh-Token']}]

            self.expiry_timestamp = int(r.headers["X-Access-Token-Expires"])

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
        
'''