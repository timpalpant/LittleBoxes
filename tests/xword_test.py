import os
import unittest

from littleboxes.xword import Crossword, XWDirection


class TestCrossword(unittest.TestCase):
    TEST_PUZZLE = os.path.join(os.path.dirname(__file__),
                               'fixtures', 'test.puz')

    def setUp(self):
        self.x = Crossword.load(open(self.TEST_PUZZLE))

    def test_load(self):
        self.assertEqual(len(self.x.clues), 138)

    def test_get_across(self):
        clue = self.x.clues[0]
        assert clue.coord.direction == XWDirection.ACROSS
        fill = self.x.get_fill(clue)
        self.assertListEqual(fill, [None, None, None, None, None])

        self.x.solution[clue.box_indices[3]] = 'A'
        fill = self.x.get_fill(clue)
        self.assertListEqual(fill, [None, None, None, 'A', None])

    def test_get_down(self):
        clue = self.x.clues[-1]
        assert clue.coord.direction == XWDirection.DOWN
        fill = self.x.get_fill(clue)
        self.assertListEqual(fill, [None, None, None])

        self.x.solution[clue.box_indices[1]] = 'A'
        fill = self.x.get_fill(clue)
        self.assertListEqual(fill, [None, 'A', None])

    def test_set(self):
        clue = self.x.clues[0]
        self.x.set_fill(clue, 'HELLO')
        fill = self.x.get_fill(clue)
        self.assertListEqual(fill, ['H', 'E', 'L', 'L', 'O'])


if __name__ == "__main__":
    unittest.main()
