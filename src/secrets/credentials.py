import configparser
import os
import json

cred = configparser.ConfigParser()
cred.read(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'secrets.ini'))

ws_account_ids = dict()
try:
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ws_account_ids.json')) as f:
        ws_account_ids = json.load(f)
except FileNotFoundError as err:
    print(err)

INTRINIO_API_KEY = cred['intrinio']['api_key']
INTRINIO_BASE_URL = cred['intrinio']['base_url']

IEX_API_KEY = cred['iex']['api_key']
IEX_BASE_URL = cred['iex']['base_url']

ALCAPA_API_KEY = cred['alpaca']['api_key']
ALCAPA_ENDPOINT = cred['alpaca']['endpoint']
ALCAPA_SECRET_KEY = cred['alpaca']['secret_key']

EMAIL_ADDRESS = cred['email_notification']['email_address']
EMAIL_PASSWORD = cred['email_notification']['email_password']

WSIMPLE_USERNAME = cred['wealth_simple']['email']
WSIMPLE_PASSWORD = cred['wealth_simple']['password']

YAHOO_FINANCE_API_KEY = cred['yahoo_finance']['api_key']
YAHOO_FINANCE_RAPID_API_HOST = cred['yahoo_finance']['x_rapidapi_host']

if __name__ == '__main__':
    pass
