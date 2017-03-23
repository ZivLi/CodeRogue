import math


def isprime(x):
	for i in range(2, int(math.sqrt(x))+2):
		if x % i == 0:
			return False
		return True


def f(n):
	count = 0
	for i in range(1, n):
		if isprime(i):
			print i
			count += 1
	print count


if __name__ == '__main__':
	while True:
		n = int(raw_input())
		if n == 0:
			break
		f(n)