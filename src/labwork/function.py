from random import random


def testfunc():
    return [random()]


if __name__ == '__main__':
    tung = testfunc()
    for _ in range(20):
        print(tung)
