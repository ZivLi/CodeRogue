import numpy as np
import pydot
from sklearn.datasets import load_iris
from sklearn import tree
from sklearn.externals.six import StringIO

iris = load_iris()
for i in range(len(iris.target)):
    print 'Example %d: label %s, features %s' % (i, iris.target[i], iris.data[i])
test_idx = [0, 50, 100]

def main():
    train_target = np.delete(iris.target, test_idx)
    train_data = np.delete(iris.data, test_idx, axis=0)

    test_target = iris.target[test_idx]
    test_data = iris.data[test_idx]

    clf = tree.DecisionTreeClassifier()
    clf.fit(train_data, train_target)

    print test_target
    print clf.predict(test_data)

    dot_data = StringIO()
    tree.export_graphviz(clf,
                         out_file=dot_data,
                         feature_names=iris.feature_names,
                         class_names=iris.target_names,
                         filled=True, rounded=True,
                         impurity=False)
    graph = pydot.graph_from_dot_data(dot_data.getvalue())
    graph.write_pdf("iris_decision_tree.pdf")

if __name__ == '__main__':
    main()
