class HashMap(object):

    def __init__(self, hash_fn, length=100):
        assert hasattr(hash_fn, '__call__'),

        self._buckets = [None] * length
        self.hash_len = length
        self.hash_fn = hash_fn
        self.change_len = length / 5


    def _hash(self, key):
        return self.hash_fn(key) % self.hash_len


    def put(self, key, val):
        pos = self._hash(key)
        bucket = self._buckets[pos]

        if bucket is None:
            self._buckets[pos] = bucket = LinkedList()
            bucket.put(key, val)
        else:
            bucket.put(key, val)
            if len(bucket) >= self.change_len:
                self._grow()


    def _grow(self):
        self.hash_len = self.hash_len * 2
        self.change_len = self.hash_len / 5

        oldBuckets = self._buckets
        self._buckets = [None] * self.hash_len

        for bucket in oldBuckets:
            if bucket is None: continue
            for (key, val) in bucket:
                self.put(key, val)


    def get(self, key):
        pos = self._hash(key)
        bucket = self._buckets[pos]

        if bucket is None: return None

        return bucket.get(key)


    def delete(self, key):
        pos = self._hash(key)
        node = self._buckets[pos]

        if node is None: return None

        self._buckets[pos] = None
        self.num_vals -= 1

        return node.val


    def _shrink(self):
        pass


    def __repr__(self):
        return '<Hashmap %r>' % self._buckets


    def __len__(self):
        n = 0
        for bucket in self._buckets:
            if bucket is None: continue
            n += len(bucket)
        return n


    def get_num_empty_buckets(self):
        n = 0
        for bucket in self._buckets:
            if bucket is None or len(bucket) == 0: n += 1
        return n


    def get_longest_bucket(self):
        longest = 0
        b = None
        for bucket in self._buckets:
            if bucket is None: continue

            l = len(bucket)
            if longest < l:
                longest = l
                b = bucket
        return longest


    def get_shortest_bucket(self):
        shortest = 0
        b = None
        for bucket in self._buckets:
            if bucket is None:
                shortest = 0
                b = None
                break

            l = len(bucket)
            if shortest == 0: shortest = l
            if shortest >= l:
                shortest = l
                b = bucket
        return shortest
