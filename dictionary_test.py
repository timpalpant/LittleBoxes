'''
Created on Dec 31, 2015

@author: justinpalpant
'''
import unittest, logging, time, sys
from dictionary import Dictionary, Trie

performance_test = False
logging.basicConfig(level=logging.INFO, stream=sys.stdout)

class TestDictionary(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        #Set up logging
        cls.logger = logging.getLogger('TestDictionary.logger')
        
        #Instance setup
        cls.dictionary_file = 'data/dictionaries/ospd3.txt'
        cls.dictionary = Dictionary.load(cls.dictionary_file, fast=True)
        cls.words = sorted([Dictionary._normalize_word(w) for w in open(cls.dictionary_file)])     
        
        
        cls.logger.debug('List requires %d bytes',sys.getsizeof(cls.words))
        
    def setUp(self):
        #Timing start
        self.start = time.time()
        self.perfiters = 1000

    def tearDown(self):
        self.logger.debug('%s: Test completed in %0.3f seconds', self.id(), time.time()-self.start)

    def test_trie_versus_dictionary_size(self):
        self.trie = Trie()
        
        for w in self.words:
            self.trie.add(w)
        
        self.assertEqual(self.trie.size, self.dictionary.size)
        
        self.logger.info('Storage size test: single Trie uses %d nodes, '
                'Dictionary uses %d nodes', self.trie.node_count, 
                self.dictionary.nodes)
        pass

    @unittest.skipIf(performance_test, 'Only running performance tests')
    def test_size(self):
        #Test-level logging
        self.assertEqual(self.dictionary.size, len(self.words))
        self.logger.info('Dictionary size: %d',self.dictionary.size)

    @unittest.skipIf(performance_test, 'Only running performance tests')
    def test_is_word_for_all_words(self):
        for w in self.words:
            self.assertTrue(self.dictionary.is_word(w), '{} not in the Dictionary'.format(w))
    
    @unittest.skipIf(performance_test, 'Only running performance tests')
    def test_nonexistence_of_nonwords(self):
        '''This is important but I don't know how to generate nonwords well'''
        pass
    
    @unittest.skipIf(performance_test, 'Only running performance tests')
    def test_enumeration_of_all_words_in_dictionary(self): 
        dict_list = sorted(list(self.dictionary))  
        self.assertListEqual(dict_list, self.words)

    @unittest.skipIf(performance_test, 'Only running performance tests')    
    def test_get_words_with_length(self):
        max_length = max(len(w) for w in self.words)
        
        for i in range(2, max_length):
            list_trie = self.dictionary.get_words(length=i)
            list_file = [w for w in self.words if len(w)==i]
            self.assertListEqual(list_trie, list_file)
            for w in list_trie:
                self.assertEqual(len(w), i)

    def test_performance_get_words_with_length(self):        
        max_length = max(len(w) for w in self.words)
        t = [0,0]
        
        for _ in range(self.perfiters):
            
            start = time.time()
            for i in range(2, max_length):
                [w for w in self.words if len(w)==i]
            t[0] += time.time()-start
                
            start = time.time()
            for i in range(2, max_length):
                self.dictionary.get_words(length=i)
            t[1] += time.time()-start

        self.logger.info('Length selection test: List comprehension, %0.4f '
                'seconds; Dictionary, %0.4f seconds', t[0], t[1])

    @unittest.skipIf(performance_test, 'Only running performance tests')
    def test_get_words_with_pattern(self):
        
        patterns = [{4:'E', 1:'C'}]
            
        for p in patterns:
            list_trie = sorted(list(self.dictionary.get_words(pattern=p)))
            list_select = self.restrict(self.words, p)

            self.assertListEqual(list_trie, list_select)
            
            for w in list_trie:
                #test that all words satisfy the pattern
                for idx, letter in p.items():
                    self.assertEqual(w[idx], letter)

    def test_performance_get_words_with_pattern(self):
        patterns = [{0:'A', 1:'B'}, {0:'C', 1:'H', 3:'Z'}]
        
        t = [0,0]
        
        for _ in range(self.perfiters):
            
            start = time.time()
            for p in patterns:
                self.restrict(self.words, p)
            t[0] += time.time()-start
                
            start = time.time()
            for p in patterns:
                self.dictionary.get_words(pattern=p)
            t[1] += time.time()-start

        self.logger.info('Pattern matching test: List comprehension, %0.4f '
                'seconds; Dictionary, %0.4f seconds', t[0], t[1])
    
    def test_performance_pattern_and_length(self):
        patterns = [{0:'A', 1:'B'}, {0:'C', 1:'H', 3:'Z'}]
        lengths = [7,8]
        
        t = [0,0]
        
        for _ in range(self.perfiters):
            
            start = time.time()
            for p,l in zip(patterns, lengths):
                words = self.restrict(self.words, p)
                [w for w in words if len(w)==l]
            t[0] += time.time()-start
                
            start = time.time()
            for p,l in zip(patterns, lengths):
                self.dictionary.get_words(pattern=p, length=l)
            t[1] += time.time()-start

        self.logger.info('Length and pattern matching test: List comprehension,'
                ' %0.4f seconds; Dictionary, %0.4f seconds', t[0], t[1])
    
    def restrict(self, wordslist, pattern):
        '''Brute force restrict a list of words to match a pattern'''
        
        for pos, letter in pattern.items():
            nextlist = []
            
            for w in wordslist:
                try:
                    if w[pos]==letter:
                        nextlist.append(w)
                except IndexError:
                    pass
            
            wordslist = nextlist
        
        return wordslist

if __name__ == "__main__":
    unittest.main()

