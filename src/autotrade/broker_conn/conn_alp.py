
from src.secrets.credentials import ALCAPA_SECRET_KEY, ALCAPA_ENDPOINT, ALCAPA_API_KEY
from src.utility.singleton import SingletonMeta
import alpaca_trade_api as alp
from alpaca_trade_api.common import URL


class ConnectionAlpaca(metaclass=SingletonMeta):
    def __init__(self, apikey: str = ALCAPA_API_KEY, secret_key: str = ALCAPA_SECRET_KEY,
                 endpoint: str = ALCAPA_ENDPOINT):
        self._conn = alp.REST(apikey, secret_key, URL(endpoint))

    @property
    def conn(self):
        return self._conn


if __name__ == '__main__':
    alpaca = ConnectionAlpaca()
    account = alpaca.conn.get_account()
    print(account)
    alpaca.conn.submit_order(symbol='TSLA',
                     qty=1,
                     side='buy',
                     time_in_force='day',
                     type='limit',
                     limit_price='400.00',
                     client_order_id='002')
