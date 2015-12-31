'''
Created on Dec 27, 2015

@author: justinpalpant
'''
import logging, collections
    
class Trie:
    '''
    Stores a dictionary of words in order to provide efficient pattern matching
    with a small memory footprint.
    
    Reference: https://en.wikipedia.org/wiki/Trie
    '''    
    def __init__(self):
        self.root = Node('', None)
        self.size = 0
    
    @classmethod   
    def load(cls, filename):
        '''Load a line-delineated text file'''
        dictionary = cls()
        
        with open(filename) as dictfile:
            for line in dictfile:
                dictionary.add(line.rstrip('\n\r'))
        
        return dictionary

    def __iter__(self):
        return self.get_words()

    def is_word(self, word):
        '''Checks for the existence of word in the trie
        
        Inputs:
            word: a string to check
        Outputs:
            A boolean indicating whether or not that word is found in the trie
        '''
        node = self.root
        logging.debug('Looking for '+self._normalize_word(word))
        
        for char in self._normalize_word(word):
            try:
                node = node.children[char]
            except KeyError:
                logging.debug(char+' is not found as a child of '+str(node))
                return False
            else:
                logging.debug(char+' is found in the trie')

        logging.debug(str(node)+' word status: '+str(node.is_word))
        return node.is_word
            
    
    def get_words(self, **kwargs):
        '''Returns all words matching pattern and length in the dictionary
        
        Inputs:
            None required, necessarily
        Keyword Arguments:
            start_node: used for recursion.  If None, defaults to the Trie root
            length: specifies the length of all words to be returned.  If not 
                specified, returns all words regardless of length that match pattern
            pattern: a dict mapping integers to letters, where the integer is
                the location of the letter in the string.  If not given, returns 
                all words of length
            e.g. 
                length=7, pattern={0:'c', 3:'q', 4:'u'} would match 'cumquat' 
                and any other words following c__qu__ (length 7)
        Outputs:
            A generator that iterates over all strings in lexical order
        '''
        node = kwargs.get('start_node', self.root)
        pattern = kwargs.get('pattern', {})
        length = kwargs.get('length', 0)
        
        #basecase
        if (node.depth == length-1 or length is 0) and node.is_word:
            yield str(node)
            
        #recursion
        result = collections.deque()
        if length is 0 or node.depth < length-1:
            if node.depth+1 in pattern: #if there is a letter specified for the next node
                try:
                    child = node.children[pattern[node.depth+1]]
                    for w in self.get_words(start_node=child, 
                            pattern=pattern, length=length):
                        yield w
                    #recurse on the one valid child matching pattern
                except KeyError: 
                    #we already know there was a pattern for the next letter
                    #therefore, nothing matches the pattern, end of recursion
                    pass
                    
            else: #no pattern restriction; recurse on all children
                for key in sorted(node.children):
                    child = node.children[key]
                    logging.debug('Fetching words matching '+str(pattern)+
                            ' of length'+str(length)+'starting at node '+
                            str(child))
                    for w in self.get_words(start_node=child, 
                            pattern=pattern, length=length):
                        yield w
    
    def add(self, word):
        '''Adds a word (string only) to the Trie'''
        currentnode = self.root

        for char in self._normalize_word(word):
            if char not in currentnode.children:
                currentnode.children[char] = Node(char, currentnode)
            
            currentnode = currentnode.children[char]
            
        if not currentnode.is_word:
            currentnode.is_word = True
            self.size += 1
    
    def _normalize_word(self, word):
        return word.upper()
    
class Node:
    '''classdocs here'''
    
    def __init__(self, char, p):
        '''init docs here'''
        self.children = {}
        self.letter = char
        self.parent = p
        self.is_word = False
        
        if p is None:
            self.depth = -1 #root is a start-of-string marker, not a character
        else:
            self.depth = p.depth + 1
        
    def __str__(self):
        return self._prefix() + self.letter
    
    def __repr__(self):
        return self.__str__()
    
    def _prefix(self):
        prefix = ''
        node = self
        while node.parent:
            prefix = node.parent.letter + prefix
            node = node.parent
            
        return prefix