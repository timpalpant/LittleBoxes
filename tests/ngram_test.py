import unittest

from littleboxes.ngram_model import NgramModel


class TestNgramModel(unittest.TestCase):
    WORDS = ['the', 'cat', 'in', 'the', 'hat']

    def setUp(self):
        self.model = NgramModel(self.WORDS, 3)

    def test_p(self):
        # 2 instances of T-H-E.
        self.assertEqual(self.model.p('the'), 0.07407407407407407)
        # 1 instance of -C-A.
        self.assertEqual(self.model.p((None, 'c', 'a')), 0.038461538461538464)
        # 2 instances of H-E-.
        self.assertEqual(self.model.p(('h', 'e', None)), 0.07407407407407407)
        # OOV -> 1 instance by smoothing.
        self.assertEqual(self.model.p('oov'), 0.038461538461538464)
        with self.assertRaises(ValueError):
            self.model.p('invalid3gram')

    def test_most_likely(self):
        self.assertEqual(self.model.most_likely('th'), 'e')
        self.assertEqual(self.model.most_likely('ca'), 't')
        self.assertEqual(self.model.most_likely('he'), None)
