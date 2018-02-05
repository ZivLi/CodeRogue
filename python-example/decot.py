import functools


def log(text):
	def decorator(func):
		@functools.wraps(func)
		def wrapper(*args, **kw):
			print '%s %s:' % (text, func.__name__)
			return func(*args, **kw)
		return wrapper
	return decorator

def dlog(func):
	def wrapper(*args, **kw):
		print 'name: %s ' % func.__name__
		return func(*args, **kw)
	return wrapper

@dlog
def now():
	print '2016'

if __name__ == '__main__':
	f = now()
	f
