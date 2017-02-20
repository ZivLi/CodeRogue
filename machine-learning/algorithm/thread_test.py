#!/usr/bin/python
# coding: utf-8
import threading
import time
import os

def booth(tid):
    global i
    global lock
    while 1:
        lock.acquire()
        if i != 0:
            i = i - 1
            print 'windows:', tid, ', rest tickets:', i
            time.sleep(1)
        else:
            print 'thread_id', tid, 'no more tickets'
            os._exit(0)
        lock.release()
        time.sleep(1)

i = 10
lock = threading.Lock()

for _ in range(4):
    new_thread = threading.Thread(target=booth, args=(_,))
    new_thread.start()
