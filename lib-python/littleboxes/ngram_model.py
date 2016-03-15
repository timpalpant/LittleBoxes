from collections import defaultdict
import itertools


class NgramModel(object):
    '''Learn an N-gram model over the letters in @words.

    OOV N-grams are modeled by Laplace smoothing with
    the given pseudocount.
    '''
    def __init__(self, words, N=3, pseudocount=1):
        self.N = N
        self.pseudocount = 1
        self._ngram2freq = defaultdict(dict)
        self._oov2freq = defaultdict(lambda: 1.0 / 26)
        self._init_freqs(words)
        self._prefix_completion = {}
        self._init_prefixes()

    def _init_freqs(self, words):
        end = [None] * (self.N-1)
        ngram2counts = defaultdict(lambda: defaultdict(int))
        for word in words:
            augmented_word = end + list(word) + end
            for ngram in window(augmented_word, self.N):
                ngram2counts[ngram[:-1]][ngram[-1]] += 1

        for prefix, count in ngram2counts.iteritems():
            total = sum(count.itervalues()) + self.pseudocount*(26 - len(count))
            self._oov2freq[prefix] = float(self.pseudocount) / total
            for k, c in count.iteritems():
                self._ngram2freq[prefix][k] = float(c) / total

    def _init_prefixes(self):
        for ngram, counts in self._ngram2freq.iteritems():
            ml = max(counts.iterkeys(), key=lambda k: counts[k])
            self._prefix_completion[ngram] = ml

    def p(self, ngram):
        '''Return N-gram probability, i.e. the probability of seeing
        the letter ngram[-1] after ngram[:-1].
        '''
        if len(ngram) != self.N:
            raise ValueError(
                "Invalid %d-gram '%s' for %d-gram model" % (
                    len(ngram), ngram, self.N))
        ngram = tuple(ngram)
        return self._ngram2freq.get(
            ngram[:-1], {}).get(
            ngram[-1], self._oov2freq[ngram[:-1]])

    def most_likely(self, prefix):
        '''Return most likely next letter given prefix (N-1) letters.'''
        return self._prefix_completion[tuple(prefix)]


def window(seq, n=2):
    "Returns a sliding window (of width n) over data from the iterable"
    "   s -> (s0,s1,...s[n-1]), (s1,s2,...,sn), ...                   "
    it = iter(seq)
    result = tuple(itertools.islice(it, n))
    if len(result) == n:
        yield result
    for elem in it:
        result = result[1:] + (elem,)
        yield result
