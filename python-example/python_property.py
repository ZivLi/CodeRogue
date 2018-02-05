class A(object):

    def __init__(self, x):
        self.x = x


class B(A):

    @property
    def x_v(self):
        return self.x + 1


if __name__ == '__main__':
    b = B(1)
    print b.x_v
