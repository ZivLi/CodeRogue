#__author__ == 'ZivLi'
from time import ctime, sleep
import threading

def music(func):
    for i in range(2):
        print 'i was listening to music. %s. %s' % (func, ctime())
        sleep(1)

def move(func):
    for i in range(2):
        print 'I was at the movies! %s.%s' % (func, ctime())
        sleep(5)

threads = []
t1 = threading.Thread(target=music(u'taiyan'))
threads.append(t1)
t2 = threading.Thread(target=move(u'chunjiao'))
threads.append(t2)


if __name__ == '__main__':
    for t in threads:
        t.setDaemon(True)
        t.start()
    t.join()
    print 'all over %s' %ctime()
