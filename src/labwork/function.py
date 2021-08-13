import datetime
from random import random
import numpy as np

def testfunc():
    return [random()]


if __name__ == '__main__':
    '2021-08-04 15:55:00-04:00'
    utcts = datetime.datetime.utcnow().timestamp()
    ts = datetime.datetime.now().timestamp()

    print(utcts)
    print(ts)
