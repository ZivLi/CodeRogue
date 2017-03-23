from multiprocessing import Process, Pool, Queue
import os, time, random


def long_time_task(name):
	print 'Run task %s (%s)...' % (name, os.getpid())
	start = time.time()
	time.sleep(random.random()*3)
	end = time.time()
	print 'Task %s runs %0.2f seconds.' % (name, (end-start))


def run_proc(name):
	print 'Run child process %s (%s)...' % (name, os.getpid())


def write(q):
	for value in ['A', 'B', 'C']:
		print 'Put %s to queue...' % value
		q.put(value)
		time.sleep(random.random())

def read(q):
	while True:
		value = q.get(True)
		print 'Get %s from queue.' % value

if __name__ == '__main__':
	q = Queue()
	pw = Process(target=write, args=(q,))
	pr = Process(target=read, args=(q,))
	pw.start()
	pr.start()
	pw.join()
	pr.terminate()
