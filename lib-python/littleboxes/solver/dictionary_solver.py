import logging

from littleboxes.solver.clique import CliqueSolver
from littleboxes.solver.solver import Solver


class DictionarySolverBase(Solver):
    def __init__(self, dictionary):
        """Args:
            dictionary (Dictionary): Dictionary of words to use as potential fills.
        """
        self._dictionary = dictionary

    def query_answers(self, xword):
        answers = {}

        for xwclue in xword.clues:
            current = xword.get_fill(xwclue)
            if any(letter is None for letter in current):
                self.logger.debug('Finding words for: "%s" that fit: %s',
                                  xwclue, current)
                pattern = {i: letter for i, letter in enumerate(current)
                           if letter is not None}
                words = set(self._dictionary.get_words(
                    pattern=pattern, length=len(current)))
                self.logger.debug('Found %d words', len(words))
                if words:
                    answers[xwclue] = words

        n_answers = sum(len(fills) for fills in answers.itervalues())
        self.logger.debug('%d possible answers for all clues', n_answers)
        return answers


class DictionaryCliqueSolver(DictionarySolverBase, CliqueSolver):
    """Solver that finds maximal cliques of compatible dictionary words,
    like the ClueDB solver. Not really usable because graphs are too large.
    """
    logger = logging.getLogger('littleboxes.solver.DictionaryCliqueSolver')
