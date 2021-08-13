import os
from datetime import time, datetime
from dateutil import tz

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class MarketHours:

    CurrentTZ = 'America/Montreal'
    PreMarketStartTime = time(hour=8, minute=00, second=00, tzinfo=tz.gettz(CurrentTZ))
    PreMarketEndTime = time(hour=9, minute=30, second=00)
    MarketStartTime = time(hour=9, minute=30, second=00)
    MarketEndTime = time(hour=16, minute=00, second=00)
    PostMarketStartTime = time(hour=16, minute=00, second=00, tzinfo=tz.gettz(CurrentTZ))
    PostMarketEndTime = time(hour=20, minute=00, second=00, tzinfo=tz.gettz(CurrentTZ))


if __name__ == '__main__':
    dt = datetime.now().time()
    print(dt)

