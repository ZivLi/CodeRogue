#coding=UTF-8
from numpy import *
import operator
from os import listdir

def createDataSet():
    """
    函数作用：构建一组训练数据（训练样本），共4个样本
    同时给出了这4个样本的标签，及labels
    """
    group = array(
        [[1.0, 1.1],
         [1.0, 1.0],
         [0, 0],
         [0, 0.1]])
    labels = ['A', 'A', 'B', 'B']
    return group, labels

def classify0(inX, dataSet, labels, k):
    '''
    shape返回矩阵的[行数, 列数],
    shape[0]获取数据集的行数
    行数就是样本的数量
    :param inX: 输入的测试样本,是一个[X, Y]样式的
    :param dataSet: 是训练样本集
    :param labels: 是训练样本标签
    :param k: TOP K最相近的
    :return:
    '''
    dataSetSize = dataSet.shape[0]

    """
    下面的求距离过程就是按照欧式距离的公式计算的.
    即 根号(x^2+y^2)
    """

    #tile属于numpy模块下边的函数
    #tile(A, reps)返回一个shape=reps的矩阵,矩阵的每个元素是A
    #这个地方就是为了把输入的样本扩展为和dataset的shape一样,然后就可以直接做矩阵减法了.
    diffMat = tile(inX, (dataSetSize, 1 )) - dataSet

    #diffMat就是输入样本与每个训练样本的差值,然后对其每个x和y的差值进行平方运算
    #矩阵**2表示对矩阵中对每个元素进行**2操作,即平方
    sqDiffMat = diffMat ** 2

    #axis=1表示按照横轴,sum表示累加,即按照行进行累加.
    sqDistances = sqDiffMat.sum(axis=1)

    distances = sqDistances ** 0.5

    #按照升序进行快速排序,返回的是原数组的下标.
    sortedDisIndicies = distances.argsort()

    #存放最终的分类结果及相应的结果投票数
    classCount = {}

    #投票过程,就是统计前k个最近的样本所属类别包含的样本个数
    for i in range(k):
        #index=sortedDistIndicies[i]是第i个最相近的样本下标
        #voteIlabel = labels[index]是样本index对应的分类结果('A' or 'B')
        voteIlabel = labels[sortedDisIndicies[i]]

        #classCount.get(voteIlabel, 0)返回voteIlabel的值,如果不存在,则返回0
        #然后将票数增加1
        classCount[voteIlabel] = classCount.get(voteIlabel, 0) + 1

    #把分类结果进行排序,然后返回得票数最多的分类结果
    sortedClassCount = sorted(classCount.iteritems(), key=operator.itemgetter(1), reverse=True)
    return sortedClassCount[0][0]

def file2matrix(filename):
    """
    从文件中读入训练数据,并存储为矩阵
    """
    fr = open(filename)
    numberOfLines = len(fr.readlines())          #获取n=样本行数
    returnMat = zeros((numberOfLines, 3))        #创建一个2维矩阵用于存放训练样本数据,一行3个数据
    classLabelVector = []                        #创建一个1维数组用于存放训练样本标签
    index = 0
    for line in fr.readlines():
        #把回车符号给去掉
        line = line.strip()
        #把每一行数据用'\t'分割
        listFromLine = line.split('\t')
        #把分割好的数据放至数据集,其中index是该样本数据的下标,就是放到第几行
        returnMat[index, :] = listFromLine[0:3]
        #把该样本对应的标签放至标签集,顺序与样本集对应.
        classLabelVector.append(int(listFromLine[-1]))
        index += 1
    return returnMat, classLabelVector

def autoNorm(dataSet):
    """
    训练数据归一化
    """

    #获取数据集中每一列的最小数值
    minVals = dataSet.min(0)
    #获取数据集中每一列的最大数值
    maxVals = dataSet.max(0)

    ranges = maxVals - minVals
    #创建一个与dataSet同shape的全0矩阵,用于存放归一化后的数据
    normDataSet = zeros(shape(dataSet))
    m = dataSet.shape[0]
    #把最小值扩充为dataSet同shape, 然后作差
    normDataSet = dataSet - tile(minVals, (m, 1))
    #把最大最小差值扩充为dataSet同shape,然后作商,是指对应元素进行除法运算,而不是矩阵除法
    #矩阵除法在numpy中要用linalg.solve(A,B)
    normDataSet = normDataSet / tile(ranges, (m, 1))
    return normDataSet, ranges, minVals


if __name__ == '__main__':
    group, labels = createDataSet()
    print classify0([0,0], group, labels, 3)
