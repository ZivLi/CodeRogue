from sklearn import tree

features = [[140, 1], [130, 1], [150, 0], [170, 0]]  # features: [weights, texture], texture: bumpy: 0, smooth: 1
labels = [0, 0, 1, 1]  # apple: 0, orange: 1

def main():
    clf = tree.DecisionTreeClassifier()
    clf = clf.fit(features, labels)
    print clf.predict([[150, 0]])

if __name__ == '__main__':
    main()
