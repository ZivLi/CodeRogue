#!/usr/bin/env python

class Attrs(object):

    def __init__(self):
        self.x = 'attrs.x'

    def set_x(self, x):
        self.x = x
        return 'run myself.'

    def get_x(self):
        return self.x

    def print_x(self):
        print 'now x is %s' % self.x


test_attrs = Attrs()

print getattr(test_attrs, 'set_x')(4)
print getattr(test_attrs, 'get_x', 'NA')
print getattr(test_attrs, 'x', 'NA')
print getattr(test_attrs, 'y', 'NA')

