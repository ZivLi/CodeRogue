from random import Random

def quick_sort(arr):
	if len(arr) > 1:
		qsort(arr, 0, len(arr)-1)

def qsort(arr, start, end):
	base = arr[start]
	pl = start
	pr = end
	while pl < pr:
		while pl < pr and arr[pr] >= base:
			pr -= 1
		if pl == pr:
			break
		else:
			arr[pl], arr[pr] = arr[pr], arr[pl]

		while pl < pr and arr[pl] <= base:
			pl += 1
		if pl == pr:
			break
		else:
			arr[pl], arr[pr] = arr[pr], arr[pl]
	
	if pl - 1 > start:
		qsort(arr, start, pl-1)
	if pr + 1 < end:
		qsort(arr, pr+1, end)

if __name__ == '__main__':
	r = Random()
	a = []
	for i in range(20):
		a.append(r.randint(0, 100))
	print a 
	quick_sort(a)
	print a
