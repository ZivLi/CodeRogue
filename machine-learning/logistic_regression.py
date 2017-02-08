from numpy import *
import matplotlib.pyplot as plt
import time


# calculate the sigmoid function
def sigmoid(inX):
    return 1.0 / (1 + exp(-inX))

def trainLogRegres(train_x, train_y, opts):
    startTime = time.time()

    numSamples, numFeatures = shape(train_x)
    alpha, maxIter = opts['alpha'], opts['maxIter']
    weights = ones((numFeatures, 1))

    # optimize through gradient descent algorilthm
    for k in xrange(maxIter):
        if opts['optimizeType'] == 'gradDescent':
            output = sigmoid(train_x * weights)
            error = train_y - output
            weights = weights + alpha * train_x.transpose() * error
        elif opts['optimizeType'] == 'stocGradDescent':
            for i in xrange(numSamples):
                output = sigmoid(train_x[i, :] * weights)
                error = train_y[i, 0] - output
                weights = weights + alpha * train_x[i, :].transpose() * error
        elif opts['optimizeType'] == 'smoothStocGradDescent':
            dataIndex = range(numSamples)
            for i in xrange(numSamples):
                alpha = 4.0 / (1.0 + k + i) + .01
                randIndex = int(random.uniform(0, len(dataIndex)))
                output = sigmoid(train_x[randIndex, :] * weights)
                error = train_y[randIndex, 0] - output
                weights = weights + alpha * train_x[randIndex, :].transpose() * error
                del(dataIndex[randIndex])
        else:
            raise NameError('Not support optimize method type')

    print 'Congratulations, training complete! Took %fs!' % (time.time() - startTime)
    return weights

def testLogRegres(weights, test_x, test_y):
    numSamples, numFeatures = shape(test_x)
    matchCount = 0
    for i in xrange(numSamples):
        predict = sigmoid(test_x[i, :] * weights)[0, 0] > 0.5
        if predict == bool(test_y[i, 0]):
            matchCount += 1
    accuracy = float(matchCount) / numSamples
    return accuracy

def showLogRegres(weights, train_x, train_y):
    numSamples, numFeatures = shape(train_x)
    if numFeatures != 3:
        print 'Sorry! I can not draw because the dimension of your data is not 2!'
        return 1

    for i in xrange(numSamples):
        if int(train_y[i, 0]) == 0:
            plt.plot(train_x[i, 1], train_x[i, 2], 'or')
        elif int(train_y[i, 0]) == 1:
            plt.plot(train_y[i, 1], train_y[i, 2], 'ob')

    min_x = min(train_x[:, 1])[0, 0]
    max_x = max(train_x[:, 1])[0, 0]
    weights = weights.getA()
    y_min_x = float(-weights[0] - weights[1] * min_x) / weights[2]
    y_max_x = float(-weights[0] - weights[1] * max_x) / weights[2]
    plt.plot([min_x, max_x], [y_min_x, y_max_x], '-g')
    plt.xlabel('X1')
    plt.ylabel('X2')
    plt.show()

def loadData(filePath):
    train_x = []
    train_y = []
    fileIn = open(filePath)
    for line in fileIn.readlines():
        lineArr = line.strip().split()
        train_x.append([1.0, float(lineArr[0]), float(lineArr[1])])
        train_y.append(float(lineArr[2]))
    return mat(train_x), mat(train_y).transpose()

def main(filePath):
    train_x, train_y = loadData(filePath)
    test_x = train_x
    test_y = train_y
    opts = {'alpha': .01, 'maxIter': 20, 'optimizeType': 'smoothStocGradDescent'}
    optimalWeights = trainLogRegres(train_x, train_y, opts)
    accuracy = testLogRegres(optimalWeights, test_x, test_y)
    showLogRegres(optimalWeights, train_x, train_y)

if __name__ == '__main__':
    _path = None
    main(_path)
