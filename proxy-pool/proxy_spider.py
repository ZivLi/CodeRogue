# coding: utf-8
import redis
import requests
import time
import threading


MAX_TIME_OUT = 5
TEST_URL = 'http://www.miaopai.com'
PROXIES = []
PROXY_URL = 'http://123.207.35.36:5010/get/'  # SOURCE FROM GITHUB.
cache = redis.Redis(host='cache', port=6379, db=1)  # TODO CHANGE ME.


class ProxyCrawl(object):

    def __init__(self):
        self.proxies = []

    @staticmethod
    def is_valid_proxy(proxy):
        proxy = {'http': 'http://' + proxy}
        try:
            response = requests.get(TEST_URL, proxies=proxy, timeout=MAX_TIME_OUT)
        except Exception as e:
            return False
        else:
            return response.status_code is 200

    def get_proxy(self):
        r = requests.get(PROXY_URL)
        proxy = r.content
        if self.is_valid_proxy(proxy):
            PROXIES.append(proxy)
            return proxy
        return None


def filter_proxy():
    pc = ProxyCrawel()
    proxy = None
    while proxy is None:
        proxy = pc.get_proxy()


def main():
    threads = []
    for _ in xrange(5):
        t = threading.Thread(target=filter_proxy)
        threads.append(t)

    for t in threads:
        t.setDaemon(True)
        t.start()

    for t in threads:
        t.join()

    save_cache()


def save_cache():
    cache.lpush('proxies', *PROXIES)
    print 'finish.'


if __name__ == '__main__':
    s = time.time()
    main()
    print PROXIES
    print time.time() - s
