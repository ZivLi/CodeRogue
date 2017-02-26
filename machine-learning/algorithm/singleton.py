"""
method 1.
"""
class Singleton(object):
    def __new__(cls, *args, **kw):
        if not hasattr(cls, '_instance'):
            cls._instance = super(Singleton, cls).__new__(cls, *args, **kw)
        return cls._instance

"""
method 2.
"""
class Bory(object):
    _state = {}
    def __new__(cls, *args, **kw):
        ob = super(Bory, cls).__new__(cls, *args, **kw)
        ob.__dict__ = cls._state
        return ob

"""
method 3.
"""
class Singleton2(type):
    def __init__(cls, name, bases, dict):
        super(Singleton2, cls).__init__(name, bases, dict)
        cls._instance = None
    
    def __call__(cls, *args, **kw):
        if cls._instance is None:
            cls._instance = super(Singleton2, cls).__call__(*args, **kw)
        return cls._instance

class Test(object):
    __metaclass__ = Singleton2
    pass

"""
method 4.
"""
def Singleton(cls, *args, **kw):
    instance = {}
    def _singleton():
        if cls not in instance:
            instance[cls] = cls(*args, **kw)
        return instance[cls]
    return _singleton

@singleton
class Test2(object):
    pass
