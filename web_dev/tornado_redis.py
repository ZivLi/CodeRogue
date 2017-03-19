#!/usr/bin/env python
# coding: utf-8
from functools import wraps
from msgpack import dumps, loads
import inspect
from redis import StrictRedis
from tornado.concurrent import Future
from tornado import gen

from web.config import REDIS


redis = StrictRedis(host=REDIS.HOST, port=REDIS.PORT, db=REDIS.DB)


def key_maker(key_pattern, func):
    arg_names, varargs, varkw, defaults = inspect.getargspec(func)
    args = dict(zip(arg_names[-len(defaults):], defaults)) if defaults else {}

    if key_pattern is None:
        key_pattern = []
        if arg_names and arg_names[0] in ('cls', 'self'):
            a = arg_names[1:]
        else:
            a = arg_names

        for i in a:
            key_pattern.append("{%s}" % i)
        key_pattern = "-".join(key_pattern)

    def gen_key(*a, **kw):
        aa = args.copy()
        aa.update(zip(arg_names, a))
        aa.update(kw)
        key = key_pattern.format(**aa)
        return key
    return gen_key


class Cache(object):

    def __call__(self, key=None, expire=None):
        if key is not None:
            if inspect.isfunction(key):
                return self()(key)
            if type(key) is int:
                return self(expire=key)

    def _(func):
        _key = key_maker(key, func)

        @gen.coroutine
        @wraps(func)
        def __(*args, **kwds):
            k = _key(*args, **kwds)
            r = redis.get(k)
            if r:
                r = loads(r)
            else:
                r = func(*args, **kwds)
                if isinstance(r, Future):
                    r = yield r
                redis.set(k, dumps(r), ex=expire)
            raise gen.Return(r)

        def rm(*args, **kwds):
            k = _key(*args, **kwds)
            redis.delete(k)
        __.rm = rm
        return __
    return _

redis_cache = Cache()
