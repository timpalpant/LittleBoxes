import logging
from networkx import find_cliques

from littleboxes.solver.clique import build_conflict_graph
from littleboxes.solver.solver import Solver


class ClueDBCliqueSolver(Solver):
    """Solver that looks for clue matches in the provided database."""

    logger = logging.getLogger('littleboxes.solver.ClueDBCliqueSolver')

    def __init__(self, db, clue_threshold=1.0):
        """Args:
            db (ClueDB): The database of clues to search for answers.
            clue_threshold (float, 0.0-1.0): Clues will be considered a match if
                they have this much N-gram similarity.
        """
        self._db = db
        self._clue_threshold = clue_threshold

    def solve(self, xword):
        '''Graph-based search for partial solutions to a crossword

        This implementation creates a graph describing possible words to play
        on the puzzle, nodes being words and the place to play them, and edges
        connecting words that can be played together without conflicts.

        Arguments:
            xword - a Crossword to be solved

        Yields:
            sorted list of tuples (prob, Crossword) of partially solved
            Crosswords in order from most- to least-solved with prob=1.0 for
            each Crossword for now
        '''
        self.logger.info('Looking up answers in ClueDB')
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

    def query_answers(self, xword):
        '''From the self._db fetch all possible answers to all clues in xword

        Arguments:
            xword - a Crossword

        Returns:
            dict(littleboxes.xword.XWClue: set(str))

        '''
        answers = {}

        for xwclue in xword.clues:
            all_answers = set()
            self.logger.debug('Finding clues within %f of %r', self._clue_threshold, xwclue.text)
            for clue, similarity in self._db.search(xwclue.text, self._clue_threshold):
                db_answers = self._db.answers(clue, len(xwclue.box_indices))
                self.logger.debug('%d possible answers for %r', len(db_answers), clue)
                all_answers.update(db_answers)
            if all_answers:
                answers[xwclue] = all_answers

        return answers
