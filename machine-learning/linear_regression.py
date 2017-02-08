# import numpy as np
import matplotlib.pyplot as plt
from numpy.linalg import inv
from numpy import dot, transpose
from matplotlib.font_manager import FontProperties
from sklearn.linear_model import LinearRegression
font = FontProperties(fname="~/Document/test1.xlsx", size=10)


if __name__ == '__main__':
    # plt.figure()
    # plt.xlabel("diameter")
    # plt.ylabel("price")
    # plt.axis([0, 25, 0, 25])

    # X = [[6], [8], [10], [14], [18]]
    # y = [[7], [9], [13], [17.5], [18]]
    # X2 = [[0], [10], [14], [25]]
    # model = LinearRegression()
    # model.fit(X, y)
    # y2 = model.predict(X2)
    # yr = model.predict(X)
    # X_test = [[8], [9], [11], [16], [12]]
    # y_test = [[11], [8.5], [15], [18], [11]]
    # print model.score(X_test, y_test)

    # for idx, x in enumerate(X):
    #     plt.plot([x, x], [y[idx], yr[idx]], 'r-')
    # plt.plot(X, y, 'k.')
    # plt.plot(X2, y2, 'g-')
    # print np.var([6, 8, 10, 14, 18], ddof=1)
    # print "residual sum of squares: %.2f"\
    #     % np.mean((model.predict(X) - y) ** 2)
    # plt.show()

    X = [[6, 2], [8, 1], [10, 0], [14, 2], [18, 0]]
    y = [[7], [9], [13], [17.5], [18]]
    model = LinearRegression()
    model.fit(X, y)
    X_test = [[8, 2], [9, 0], [11, 2], [16, 2], [12, 0]]
    y_test = [[11], [8.5], [15], [18], [11]]
    predictions = model.predict(X_test)
    for i, prediction in enumerate(predictions):
        print ("Predicted: %s, Target: %s" % (prediction, y_test[i]))
    print "R-squared: %.2f" % model.score(X_test, y_test)
