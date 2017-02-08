from __future__ import print_function
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from collections import defaultdict
from string import punctuation
from heapq import nlargest

stopwords = set(stopwords.words('english') + list(punctuation))
max_cut = 0.9; min_cut = 0.1


def compute_frequencies(word_sent):
    freq = defaultdict(int)

    for s in word_sent:
        for word in s:
            if word not in stopwords:
                freq[word] += 1

    m = float(max(freq.values()))
    for w in list(freq.keys()):
        freq[w] = freq[w] / m
        if freq[w] >= max_cut or freq[w] <= min_cut:
            del freq[w]
    return freq


def summarize(text, n):
    sents = sent_tokenize(text)
    assert n <= len(sents)

    word_sent = [word_tokenize(s.lower()) for s in sents]
    freq = compute_frequencies(word_sent)
    ranking = defaultdict(int)
    for i, word in enumerate(word_sent):
        for w in word:
            if w in freq:
                ranking[i] += freq[w]
    sents_idx = rank(ranking, n)
    return [sents[j] for j in sents_idx]


def rank(ranking, n):
    return nlargest(n, ranking, key=ranking.get)


if __name__ == '__main__':
    with open("news.txt", "r") as f:
        text = f.read().replace('\n', '')
    res = summarize(text, 4)
    for i in range(len(res)):
        print("* " + res[i])
