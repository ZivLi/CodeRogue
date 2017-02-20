# coding: utf-8
from multiprocessing import Pool, Queue
import multiprocessing, random
import os, time

def long_time_task(name):
    print 'Run task %s (%s)...' % (name, os.getpid())
    start = time.time()
    time.sleep(2)
    end = time.time()
    print 'Task %s runs %.2f seconds.' % (name, (end-start))

def write(q):
    for value in ['a', 'b', 'c', 'd']:
        print 'Put %s to queue.' % value
        q.put(value)
        time.sleep(random.random())

def read(q, lock):
    while 1:
        lock.acquire()
        if not q.empty():
            value = q.get(True)
            print 'Get %s from queue' % value
            time.sleep(random.random())
        else:
            break
        lock.release()


if __name__ == '__main__':
    # print 'Parent process %s.' % os.getpid()
    # p = Pool()
    # for i in range(4):
    #     p.apply_async(long_time_task, args=(i,))
    # print 'Waiting for all subprocesses done...'
    # p.close()
    # p.join()
    # print 'All subprocesses done.'

    manager = multiprocessing.Manager()
    q = manager.Queue()
    p = Pool()
    lock = manager.Lock()
    pw = p.apply_async(write, args=(q, ))
    pr = p.apply_async(read, args=(q, lock))
    p.close()
    p.join()
    print
    print 'all done.'
