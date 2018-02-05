#nowcoder .py
#__author__ == 'ZivLi'

#NO.1
# a = [[1, 2, 3], [4, 5, 6], [7, 8, 9], [10, 11, 12]]
def Find(array, target):
    x = 0
    y = len(array[0]) - 1

    while (x <= len(array) - 1 and y >= 0):
        if target < array[x][y]:
            y -= 1
        elif target > array[x][y]:
            x += 1
        else:
            return True
    return False

#NO.2
# s = 'We Are Happy'
def replaceSpace(s):
    return s.replace(" ", str("%20"))

#NO.3
# class ListNode:
#     def __init__(self, x):
#         self.val = x
#         self.next = None
def printListFromTailToHead(listNode):
    result = []
    if listNode is None:
        return result

    while listNode.next is not None:
        result.extend([listNode.val])
        listNode = listNode.next
    result.extend([listNode.val])
    return result[::-1]

# a = [[1,2,3,4], [5,6,7,8], [9,10, 11, 12], [13,14,15,16]]
def printMatrix(matrix):
    result = []
    i, j, flag = 0, 0, 0
    top, bottom, left, right = 0, len(matrix)-1, 0, len(matrix[0])-1
    while True:
        if matrix is None:
            return result
        if top > bottom or left > right:
            break
        result.append(matrix[i][j])
        if flag % 4 == 0:
            if j < right:
                j += 1
            else:
                i += 1
                flag += 1
                top += 1
        elif flag % 4 == 1:
            if i < bottom:
                i += 1
            else:
                j -= 1
                flag += 1
                right -= 1
        elif flag % 4 == 2:
            if j > left:
                j -= 1
            else:
                i -= 1
                flag += 1
                bottom -= 1
        else:
            if i > top:
                i -= 1
            else:
                j += 1
                flag += 1
                left += 1
    return result


def NumberOf1(n):
    import math
    x = n & int(math.pow(2, 32) - 1)
    return bin(x).count("1")


def BAT1():
    for i in range(input()):
        s = raw_input().split()
        if int(s[0]) + int(s[1]) > int(s[2]):
            print "Case #" + str(i+1) +": true"
        else:
            print "Case #" + str(i+1) +": false"


def BAT2():
    Num = raw_input().split(" ")
    a1, a2, a3, a4, a5 = [], [], [], [], []

    for x in Num[1:]:
        a = int(x)
        if x[-1] == '0': a1.append(a)
        if a % 5 == 1: a2.append(a)
        if a % 5 == 2: a3.append(x)
        if a % 5 == 3: a4.append(a)
        if a % 5 == 4: a5.append(a)

    A1 = sum(a1) if len(a1) else "N"
    for i in range(len(a2)):
        import math
        a2[i] = math.pow(-1, i) * a2[i]
    A2 = int(sum(a2)) if len(a2) else "N"
    A3 = len(a3) if len(a3) else "N"
    A4 = round(float(sum(a4)) / float(len(a4)),1) if len(a4) else "N"
    A5 = max(a5) if len(a5) else "N"
    print A1, A2, A3, A4, A5

def BAT3():
    n = raw_input().split()

    def isPrime(x):
        import math
        for i in range(2, int(math.sqrt(x))+1):
            if x % i == 0:
                return False
        return True

    result = []
    flag = 1
    if n[0] == '1' and n[1] == '1':
        print 2
    while True:
        for i in range(3, 10000000):
            if isPrime(i):
                flag += 1
                if flag >= int(n[0]) and flag <= int(n[1]):
                    result.append(i)
                elif flag > int(n[1]):
                    break
                else:
                    continue
        break

    count = 1
    for i in range(len(result)):
        if count % 10 == 0:
            print result[i]
        else:
            print result[i],
        count += 1

def BAT4():
    s = raw_input().split(",")

    def trans(s, n):
        re = ''
        st = s.split(" ")
        st = st[::-1]
        for j in range(len(st)):
            for i in range(len(st[j])):
                if st[j][i] != ' ':
                    if st[j][i].isupper():
                        re += st[j][i].lower()
                    else:
                        re += st[j][i].upper()
            re += " "
        return re[:-1]
    print trans(s[0], s[1])

def HUAWEI1():
    count = int(raw_input().split(' ')[1])
    score = raw_input().split(' ')
    while count:
        inp = raw_input().split(' ')
        op = inp[0]
        m = int(inp[1])
        n = inp[2]
        if op == 'Q':
            print max(score[m-1:int(n)-1])
        else:
            score[m] = n
        count -= 1

def Fibonacci(n):
    if n == 0:
        return 0
    elif n == 1:
        return 1
    else:
        return Fibonacci(n-1) + Fibonacci(n-2)

def Fibonacci2(n):
    a1 = 1
    a2 = 0
    if n == 0:
        return 0
    for i in range(1, n):
        tmp = a1
        a1 = a1 + a2
        a2 = tmp
    return a1

def BAT5():
    A, B = map(int, raw_input().split(" "))
    Q = A / B
    R = A % B
    print Q, R

def HUAWEI2():
    return len(raw_input().split(" ")[-1])




def TouTiao():
    string = raw_input()
    N = int(raw_input())
    while True:
        if N == 0:
            break
        else:
            M = raw_input().split(" ")
            x, y = int(M[0]), int(M[1])
            tmp = string[x:y+1]
            string += tmp[::-1]
            N -= 1
    print string

TouTiao()
