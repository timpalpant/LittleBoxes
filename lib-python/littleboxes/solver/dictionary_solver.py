import logging
from networkx import find_cliques

from littleboxes.solver.clique import build_conflict_graph
from littleboxes.solver.solver import Solver


class DictionaryCliqueSolver(Solver):
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
        possible_answers = self.query_answers(xword)
        conflict_graph = build_conflict_graph(xword, possible_answers)

        for xwsolution in find_cliques(conflict_graph):
            solved = xword.copy()
            for fill in xwsolution:
                solved.set_fill(fill.clue, fill.word)
            yield solved.n_set, solved

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

