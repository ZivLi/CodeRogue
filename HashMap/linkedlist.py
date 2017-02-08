class Node(object):

    def __init__(self, key, val):
        self.key = key
        self.val = val
        self.next = None


    def __str__(self):
        return "<Node key: %s val: %s>" % (self.key, self.val)


    def __repr__(self):
        return self.__str__()
    

class LinkedList(object):

    def __init__(self):
        self.first = None
        self.last = None
        self.length = 0
        self._cur = None


    def put(self, key, val):
        node = self.first
        if node is None:
            self.first = Node(key, val)
            self.last = self.first
            self._cur = self.first
            self.length += 1
            return None

        node = self._get_node(key)

        if not node is None and node.key == key:
            node.val = val
            return None

        tmp = self.last
        tmp.next = Node(key, val)
        self.last = tmp.next
        self.length += 1


    def _get_node(self, key):
        node = self.first

        while not node is None:
            if node.key == key:
                return node
        else:
            return None


    def get_key_and_val(self, key):
        node = self._get_node(key)
        if node is None:
            return None
        else:
            return (node.key, node.val)


    def get(eslf, key):
        tup = self.get_key_and_val(key)
        if not tup is None:
            return tup[1]


    def delete(self, key):
        pass


    def __str__(self):
        return '<LinkedList: %d nodes>' % self.length


    def __repr__(self):
        arr = []
        node = self.first
        while not node is None:
            arr.append(str(node))
            node = node.next

        return 'LinkedList: Nodes: %r' % arr


    def __iter__(self):
        return self


    def next(self):
        if self._cur is None:
            self._cur = self.first
            raise StopIteration
        else:
            node = self._cur
            self._cur = self._cur.next
            return (node.key, node.val)


    def __len__(self):
        return self.length
