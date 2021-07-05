import queue


class ThreadQueue:
    def __init__(self):
        self.q = queue.Queue()

    def enqueue(self):
        self.q.put(5)
