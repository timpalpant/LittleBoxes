import logging
from networkx import find_cliques
import random

from littleboxes.solver.clique import build_conflict_graph
from littleboxes.solver.solver import Solver


class DictionarySolverBase(Solver):
    def query_answers(self, xword):
        answers = {}

        for xwclue in xword.clues:
            current = xword.get_fill(xwclue)
            if any(letter is None for letter in current):
                pattern = {i: letter for i, letter in enumerate(current)
                           if letter is not None}
                words = list(self._dictionary.get_words(pattern=pattern, length=len(current)))
                if words:
                    answers[xwclue] = words

        return answers


class DictionaryCliqueSolver(DictionarySolverBase):
    """Solver that looks for words in the provided dictionary that
    satisfy the current constraints in the puzzle.
    """
    logger = logging.getLogger('littleboxes.solver.DictionaryCliqueSolver')

    def __init__(self, dictionary):
        """Args:
            dictionary (Dictionary): Dictionary of words to use as potential fills.
        """
        self._dictionary = dictionary

    def solve(self, xword):
        self.logger.info('Looking up answers in Dictionary')
        possible_answers = self.query_answers(xword)
        self.logger.info('Generating conflict graph')
        conflict_graph = build_conflict_graph(xword, possible_answers)

        self.logger.info('Finding cliques in conflict graph')
        for xwsolution in find_cliques(conflict_graph):
            solved = xword.copy()
            for fill in xwsolution:
                solved.set_fill(fill.clue, fill.word)
            self.logger.info('Found solution')
            yield solved.n_set, solved


class DictionaryGuessSolver(DictionarySolverBase):
    logger = logging.getLogger('littleboxes.solver.DictionaryGuessSolver')

    def __init__(self, dictionary):
        """Args:
            dictionary (Dictionary): Dictionary of words to use as potential fills.
        """
        self._dictionary = dictionary

    def solve(self, xword):
        xword = xword.copy()
        self.logger.info('Looking up answers in Dictionary')
        potential_answers = self.query_answers(xword)
        self.logger.info('Filling in answers in order of minimum entropy')
        while potential_answers:
            self.logger.debug('%d clues with potential answers', len(potential_answers))
            # Find the clue with the fewest potential answers.
            clue = min(potential_answers, key=lambda clue: len(potential_answers[clue]))
            self.logger.debug('Filling in %r with one of %d potential answers',
                             clue.text, len(potential_answers[clue]))
            # Choose one answer randomly.
            answer = random.choice(potential_answers[clue])
            xword.set_fill(clue, answer)
            self.logger.debug('Looking up answers in Dictionary')
            potential_answers = self.query_answers(xword)

        self.logger.info('Found solution')
        yield xword.n_set, xword
