from collections import OrderedDict


class LRUcache:

    def __init__(self, capacity):
        self.capacity = capacity
        self.queue = OrderedDict()

    def get(self, key):
        if key not in self.queue:
            return -1
        value = self.queue.pop(key)
        self.queue[key] = value
        return self.queue[key]

    def put(self, key, value):
        if key in self.queue:
            self.queue.pop(key)
        elif len(self.queue.items()) == self.capacity:
            self.queue.popitem(last=False)
        self.queue[key] = value
