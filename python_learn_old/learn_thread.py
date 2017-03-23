import time, threading


def loop():
	print 'thread %s is running...' % threading.current_thread().name
	n = 0
	while n < 5:
		n = n + 1
		print 'thread %s  >>> %s' % (threading.current_thread().name, n)
		time.sleep(1)
	print 'thread %s ended.' % threading.current_thread().name

balance = 0
lock = threading.Lock()

def change_it(n):
	global balance
	balance = balance + n
	balance = balance - n

def run_thread(n):
	for i in range(10000):
		lock.acquire()
		try:
			change_it(n)
		finally:
			lock.release()


if __name__ == '__main__':
	t1 = threading.Thread(target=run_thread, args=(5,))
	t2 = threading.Thread(target=run_thread, args=(8,))
	t1.start()
	t2.start()
	t1.join()
	t2.join()
	print balance

