import random
import time

def sequential_search(lis, key):
    cnt = len(lis)
    for i in range(cnt):
        if lis[i] == key:
            return i
        else:
            return False


def binary_search(l, key):
    left, right = 0, len(l) - 1
    while left < right:
        mid = int((left+right)/2)
        if key < l[mid]:
            right = mid - 1
        elif key > l[mid]:
            left = mid + 1
        else:
            return mid
    return False


class BSTNode(object):

    def __init__(self, data, left=None, right=None):
        self.data = data
        self.left = left
        self.right = right
        

class BinarySortTree:

    def __init__(self):
        self._root = None


    def is_empty(self):
        return self._root is None


    def search(self, key):
        bt = self._root
        while bt:
            entry = bt.data
            if key < entry:
                bt = bt.left
            elif key > entry:
                bt = bt.right
            else:
                return entry
        return None


    def insert(self, key):
        bt = self._root
        if not bt:
            self._root = BSTNode(key)
            return
        while True:
            entry = bt.data
            if key < entry:
                if bt.left is None:
                    bt.left = BSTNode(key)
                    return
                bt = bt.left
            elif key > entry:
                if bt.right is None:
                    bt.right = BSTNode(key)
                    return
                bt = bt.right
            else:
                bt.data = key
                return


    def delete(self, key):
        p, q = None, self._root
        if not q:
            return
        while q and q.data != key:
            p = q
            if key < q.data:
                q = q.left
            else:
                q = q.right
            if not q:
                return
        if not q.left:
            if p is None:
                self._root = q.right
            elif q is p.left:
                p.left = q.right
            else:
                p.right = q.right
            return
        r = q.left
        while r.right:
            r = r.right
        r.right = q.right
        if p is None:
            self._root = q.left
        elif p.left is q:
            p.left = q.left
        else:
            p.right = q.left


    def __iter__(self):
        stack = []
        node = self._root
        while node or stack:
            while node:
                stack.append(node)
                node = node.left
            node = stack.pop()
            yield node.data
            node = node.right


class HashTable:
    
    def __init__(self, size):
        self.elem = [None for _ in range(size)]
        self.count = size


    def hash(self, key):
        return key % self.count


    def insert_hash(self, key):
        address = self.hash(key)
        while self.elem[address]:
            address = (address + 1) % self.count
        self.elem[address] = key


    def search_hash(self, key):
        star = address = self.hash(key)
        while self.elem[address] != key:
            address = (address+1) % self.count
            if not self.ele[address] or address == star:
                return False
        return True


def insertion_search(l, key, low, high):
    mid = low + (key-l[low]) / (a[high]-a[low]) * (high-low)
    if l[mid] == key:
        return mid
    if l[mid] > key:
        return insertion_search(l, key, low, mid-1)
    else:
        return insertion_search(l, key, mid+1, high)


def main():
    lis = [random.randint(1, 1000) for _ in range(100)]
    lis.sort()
    print lis
    start = time.time()
    find_key = 83
    position = binary_search(lis, find_key)
    print position if position else -1


if __name__ == '__main__':
    main()
