'''
Created on Dec 31, 2015

@author: justinpalpant
'''
import unittest, logging
from dictionary import Trie

class TestTrie(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.dictionary_file = '/Users/new/Documents/LittleBoxes/data/dictionaries/en_short.txt'
        cls.dictionary = Trie.load(cls.dictionary_file)
        cls.words = sorted([w.rstrip('\n\r').upper() for w in open(cls.dictionary_file)])    

    def setUp(self):
        pass 
        
    def tearDown(self):
        pass

    def test_size(self):
        self.assertEqual(self.dictionary.size, len(self.words))

    def test_is_word_for_all_words(self):
        for w in self.words:
            self.assertTrue(self.dictionary.is_word(w))
            
    def test_nonexistence_of_nonwords(self):
        '''This is important but I don't know how to generate nonwords well'''
        pass

    def test_enumeration_of_all_words_in_dictionary(self):
        #self.assertListEqual(list(self.dictionary), self.words)
        
        for w1, w2 in zip(self.dictionary, self.words):
            self.assertEqual(w1, w2)
        
    def test_get_words_with_length(self):
        max_length = max(len(w) for w in self.words)
        
        for i in range(2, max_length):
            list_trie = self.dictionary.get_words(length=i)
            list_file = [w for w in self.words if len(w)==i]
            for w1, w2 in zip(list_trie, list_file):
                self.assertEqual(w1, w2)
                self.assertEqual(len(w1), i)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
            
    logging.basicConfig(level=0)
    unittest.main()