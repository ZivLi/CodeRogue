# -*- coding: utf-8 -*-
import random
import uuid
import time

def insert_sort(lists):
    """
    插入排序：
        将一个数据插入到已经排好的有序数据中。算法适用于少量数据的排序。
        时间复杂度 O(n^2)。
        稳定的排序方法。
    """
    cnt = len(lists)
    for i in range(1, cnt):
        key = lists[i]
        j = i - 1
        while j >= 0:
            if lists[j] > key:
                lists[j+1] = lists[j]
                lists[j] = key
            j -= 1
    return lists


def shell_sort(lists):
    """
    希尔排序：
        插入排序的一种。
        把记录按下标的一定增量分组，对每组使用直接插入排序算法排序，当增量减至1时，算法终止。
        非稳定排序方法。
    """
    cnt = len(lists)
    step = 2
    group = cnt / step
    while group > 0:
        for i in range(group):
            j = i + group
            while j < cnt:
                k = j - group
                key = lists[j]
                while k >= 0:
                    if lists[k] > key:
                        lists[k+group] = lists[k]
                        lists[k] = key
                    k -= group
                j += group
        group /= step
    return lists


def bubble_sort(lists):
    """
    冒泡排序:
        重复遍历数列，一次比较两个元素，如果顺序错误则交换位置。
    run_time: 0.0640749931335
    """
    cnt = len(lists)
    for i in range(0, cnt):
        for j in range(i+1, cnt):
            if lists[i] > lists[j]:
                lists[i], lists[j] = lists[j], lists[i]
    return lists


def quick_sort(arr, left, right):
    if left < right:
        pivot_index = partition(arr, left, right)
        quick_sort(arr, left, pivot_index-1)
        quick_sort(arr, pivot_index+1, right)

def partition(arr, left, right):
    pivot_index = left
    pivot = arr[left]
    for i in range(left+1, right+1):
        if arr[i] < pivot:
            pivot_index += 1
            if pivot_index != i:
                arr[pivot_index], arr[i] = arr[i], arr[pivot_index]
    arr[left], arr[pivot_index] = arr[pivot_index], arr[left]

    return pivot_index

def quick_sort(lists, left, right):
    """
    快速排序:
        通过一趟排序将要排序的数据分割成独立的两部分。其中一部分的所有数据都比另外一部分的所有数据都要小。
    排序过程递归，直到整个数列有序。
    """
    if left >= right:
        return lists
    key = lists[left]
    low = left
    high = right
    while left < right:
        while left < right and lists[right] >= key:
            right -= 1
        lists[left] = lists[right]
        while left < right and lists[left] <= key:
            left += 1
        lists[right] = lists[left]
    lists[right] = key
    quick_sort(lists, low, left-1)
    quick_sort(lists, left+1, high)
    return lists


def select_sort(lists):
    """
    直接选择排序：
        第i趟在待排序的i~n中选出最小的记录，与i交换。使有序序列不断增长直到全部排序完毕。
    run_time: 0.0359659194946
    """
    cnt = len(lists)
    for i in range(cnt):
        _min = i
        for j in range(i+1, cnt):
            if lists[_min] > lists[j]:
                _min = j
        lists[_min], lists[i] = lists[i], lists[_min]
    return lists


def heap_sort(lists):
    """
    堆排序：
        利用堆集树这种数据结构设计的排序算法。是选择排序的一种。堆分为大根和小根堆，是完全二叉树。
    run_time: 0.0056140422821
    """
    size = len(lists)
    build_heap(lists, size)
    for i in range(size)[:: -1]:
        lists[0], lists[i] = lists[i], lists[0]
        adjust_heap(lists, 0, i)
    return lists


def adjust_heap(lists, i, size):
    lchild = 2 * i + 1
    rchild = 2 * i + 2
    _max = i
    if i < size / 2:
        if lchild < size and lists[lchild] > lists[_max]:
            _max = lchild
        if rchild < size and lists[rchild] > lists[_max]:
            _max = rchild
        if _max != i:
            lists[_max], lists[i] = lists[i], lists[_max]
            adjust_heap(lists, _max, size)


def build_heap(lists, size):
    for i in range(size/2)[:: -1]:
        adjust_heap(lists, i, size)


def merge_sort(lists):
    """
    归并排序：
        比较a[i]和a[j]的大小，如果a[i]<=a[j]，则将第一个有序表中的元素a[i]复制到r[k]中，并令i和k分别加1；
    否则将第二个有序表中的元素a[j]复制到r[k]中，并令j和k分别加1，如此循环下去，直到其中一个有序表取完，然后
    将另一个有序表中剩余的元素复制到r中从下标k到下标t的单元。
        递归实现，先把待排序区间[s, t]以中点二分。
    run_time: 0.00422406196594
    """
    if len(lists) <= 1:
        return lists
    num = len(lists) / 2
    left = merge_sort(lists[:num])
    right = merge_sort(lists[num:])
    return merge(left, right)


def merge(left, right):
    i, j = 0, 0
    result = []
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    result += left[i:]
    result += right[j:]
    return result


def radix_sort(lists, radix=10):
    """
    基数排序：
        通过键值的部分资讯，将要排序的元素分配到某些桶中，以达到排序的作用。
        稳定排序。
        时间复杂度：O(nlog(r)m)
    """
    import math
    k = int(math.ceil(math.log(max(lists), radix)))
    bucket = [[] for i in range(radix)]
    for i in range(1, k+1):
        for j in lists:
            bucket[j/(radix**(i-1)) % (radix**i)].append(j)
        del lists[:]
        for z in bucket:
            lists += z
            del z[:]
    return lists


def main():
    list1 = [random.randint(1, 10000) for i in xrange(1000)]
    start = time.time()
    sort_method_list = bubble_sort(list1)
    print sort_method_list
    sorted_list = list1.sort()
    # .sort() run time: 0.000211000442505
    elapsed = (time.time() - start)
    print elapsed
    

if __name__ == '__main__':
    main()
