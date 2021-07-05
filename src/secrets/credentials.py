import configparser
import os
import json

cred = configparser.ConfigParser()
cred.read(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'secrets.ini'))

q_tokens = dict()
try:
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'qtokens.json')) as f:
        q_tokens = json.load(f)
except FileNotFoundError as err:
    print(err)

ws_tokens = dict()
try:
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'wstokens.json')) as f:
        ws_tokens = json.load(f)
except FileNotFoundError as err:
    print(err)


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
ALCAPA_BASE_URL = cred['alpaca']['base_url']
ALCAPA_SECRET_KEY = cred['alpaca']['secret_key']

EMAIL_ADDRESS = cred['email_notification']['email_address']
EMAIL_PASSWORD = cred['email_notification']['email_password']
SMTP_SSL_HOST = cred['email_notification']['smtp_ssl_host']
SMTP_SSL_PORT = cred['email_notification']['smtp_ssl_port']
IMAP_SSL_HOST = cred['email_notification']['imap_ssl_host']
IMAP_SSL_PORT = cred['email_notification']['imap_ssl_port']

QUESTRADE_TOKEN_URL = '{host}{endpoint}'.format(host=cred['questrade']['host'], endpoint=cred['questrade']['endpoint'])
QUESTRADE_TOKENS = q_tokens

WSIMPLE_EMAIL = cred['wealth_simple']['email']
WSIMPLE_PASSWORD = cred['wealth_simple']['password']
WSIMPLE_TOKENS = ws_tokens
WSIMPLE_AC_IDS = ws_account_ids

YAHOO_FINANCE_API_KEY = cred['yahoo_finance']['api_key']
YAHOO_FINANCE_RAPID_API_HOST = cred['yahoo_finance']['x_rapidapi_host']

if __name__ == '__main__':
    pass
