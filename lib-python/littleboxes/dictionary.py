'''
Created on Dec 27, 2015

@author: justinpalpant
'''
import logging
import time
import collections


class Dictionary(object):
    '''Stores a dictionary of words as a dictionary of length-binned Tries

    Requires moderate memory usage, but provides good speed for:
        Iterating over all words (equal to a list)
        Finding all words of a certain length (equal to length-binned list)
        Finding all words matching a certain pattern (faster than list)
        Finding all words of length matching pattern (MUCH faster than list)
    '''

    def __init__(self, fast=True):
        '''Creates an empty Dictionary

        Initializes logging and the dict used to store Tries. The boolean fast
        should generally be True unless memory is a serious issue (in which case
        you probably shouldn't use this class) - it causes each Trie to store a
        master list of words to speed up the special case when you want all
        words of a given length.
        '''

        self.fast = fast
        self.binned_tries = {}
        self.logger = logging.getLogger('Dictionary.logger')
        if self.fast:
            self.logger.debug('Created a FAST Dictionary')

    @classmethod
    def load(cls, istream, fast=False):
        '''Load a line-delineated text file with one word per line'''
        start = time.time()
        dictionary = cls(fast=fast)

        for line in istream:
            dictionary.add(line)

        dictionary.logger.debug('Loaded %d words into %d nodes in %0.3f seconds',
                                dictionary.size, dictionary.nodes, time.time() - start)

        return dictionary

    @property
    def nodes(self):
        return sum(t.node_count for t in self.binned_tries.values())

    @property
    def size(self):
        return sum(t.size for t in self.binned_tries.values())

    @classmethod
    def _normalize_word(cls, word):
        return word.rstrip('\n\r').upper()

    def __iter__(self):
        return self.get_words().__iter__()

    def add(self, word):
        '''Add a word to the correct Trie, or create the trie if none exists'''
        word = Dictionary._normalize_word(word)

        try:
            self.binned_tries[len(word)].add(word)
        except KeyError:
            self.binned_tries[len(word)] = Trie(fast=self.fast)
            self.binned_tries[len(word)].add(Dictionary._normalize_word(word))

    def get_words(self, **kwargs):
        '''Returns all words in the dictionary matching pattern and length

        Inputs:
            None required, necessarily
        Keyword Arguments:
            length: an integer specifying how long the word should be.  If not
                specified, any length is allowed
            pattern: a dict mapping integers to letters, where the integer is
                the location of the letter in the string.  If not given, returns 
                all words of length
            e.g. 
                pattern={0:'c', 3:'q', 4:'u'} would match 'cumquat' 
                and any other words following c__qu*
        Outputs:
            A generator that iterates over all strings by length and then in
            lexical order
        '''
        p = kwargs.get('pattern', {})
        length = kwargs.get('length', 0)
        result = []

        # lets us skip short words if pattern specifies that they be long
        if p:
            min_length = max(p)
        else:
            min_length = 0

        if length is not 0 and length in self.binned_tries:
            result.extend(self.binned_tries[length].get_words(pattern=p))

        elif length is 0:
            for l, trie in self.binned_tries.items():
                if l >= min_length:
                    result.extend(trie.get_words(pattern=p))

        return result

    def is_word(self, word):
        '''Checks the dictionary to see if it contains a word'''
        word = Dictionary._normalize_word(word)
        try:
            result = self.binned_tries[len(word)].is_word(word)
        except KeyError:
            return False

        return result


class Trie(object):
    '''
    Stores a dictionary of words in order to provide efficient pattern matching.

    Tries can store arbitrary text, and provide pattern matching efficiently.  
    In order to provide length-based lookup efficiently, see the Dictionary 
    class above, which bins words by length.  While this this requires slightly 
    more memory, the increase in lookup time for words by length is substantial 
    because it removes the need for post-processing of the Trie result.

    Reference: https://en.wikipedia.org/wiki/Trie
    '''

    def __init__(self, fast=True):
        '''Creates a root node, empty master list of words, and initializes
        logging for the Trie
        '''

        self.root = Node()
        self.fast = fast
        self.wordslist = []
        self.list_is_sorted = True
        self.size = 0
        self.node_count = 1
        self.logger = logging.getLogger('Trie.logger')
        if self.fast:
            self.logger.debug('Created a FAST Trie')

    def is_word(self, word):
        '''Checks for the existence of word in the trie

        Inputs:
            word: a string to check
        Outputs:
            A boolean indicating whether or not that word is found in the trie
        '''
        node = self.root

        for char in word:
            try:
                node = node.children[char]
            except KeyError:
                self.logger.debug(str(node) + ' word status: ' + str(False))
                return False

        self.logger.debug(str(node) + ' word status: ' + str(bool(node.word)))
        return bool(node.word)

    def __iter__(self):
        return self.get_words().__iter__()

    def get_words(self, pattern={}):
        '''Returns all words matching pattern in the dictionary using inorder 
        traversal of the Trie

        Inputs:
            None required, necessarily
        Keyword Arguments:
            pattern: a dict mapping integers to letters, where the integer is
                the index of the letter in the string.  If not given, returns 
                all words
            e.g. 
                pattern={0:'c', 3:'q', 4:'u'} would match 'cumquat' 
                and any other words following c__qu.*
        Outputs:
            A list of words in the Trie in lexical order
        '''
        stack = collections.deque()
        node = self.root
        depth = -1

        result = []

        # special case for high-memory speedup by storing a list of all words
        if self.fast and not pattern:
            if self.list_is_sorted:
                return self.wordslist
            else:
                self.wordslist.sort()
                self.list_is_sorted = True
                return self.wordslist

        try:
            min_depth = max(pattern)
        except ValueError:
            min_depth = 0

        while node or stack:
            if not node:
                depth, node = stack.popleft()

            if node.word and depth >= min_depth:
                self.logger.debug('%s matches ' + str(pattern), str(node))
                result.append(node.word)

            if depth + 1 in pattern:
                try:
                    node = node.children[pattern[depth + 1]]
                    depth += 1
                except KeyError:  # no valid child for pattern
                    node = None

            # No pattern - pick alphabetically and queue all other children
            else:
                try:
                    letters = sorted(node.children.keys())
                    nextnode = node.children[letters[0]]
                    depth += 1
                    for c in reversed(letters[1:]):
                        stack.appendleft((depth, node.children[c]))
                    node = nextnode

                except IndexError:  # no children
                    node = None

        return result

    def add(self, word):
        '''Adds a word (string only) to the Trie'''
        currentnode = self.root

        for char in word:
            if char not in currentnode.children:
                currentnode.children[char] = Node()
                self.node_count += 1

            currentnode = currentnode.children[char]

        if not currentnode.word:
            currentnode.word = word
            self.size += 1
            self.logger.debug('Adding %s to the Trie', word)
            if self.fast:
                self.wordslist.append(word)
                self.list_is_sorted = False

                self.logger.debug(
                    'Also adding %s to the fast lookup list', word)
        else:
            self.logger.debug('%s was already in the Trie', word)
            pass


class Node(object):
    '''Small Node class for use in Trie'''

    def __init__(self):
        '''Creates an empty node and empty dictionary of children'''
        self.children = {}
        self.word = None

    def __str__(self):
        if self.word:
            return self.word
        else:
            return 'Node does not contain a word'

    def __repr__(self):
        return self.__str__()
