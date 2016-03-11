import logging
from networkx import find_cliques

from littleboxes.solver.clique import build_conflict_graph
from littleboxes.solver.solver import Solver


class ClueDBCliqueSolver(Solver):
    """Solver that looks for clue matches in the provided database."""

    logger = logging.getLogger('littleboxes.solver.ClueDBCliqueSolver')

    def __init__(self, db, distance_cutoff=0):
        """Args:
            db (ClueDB): The database of clues to search for answers.
            distance_cutoff (int): Clues will only be considered a match if 
                they have Levenstein distance <= cutoff. Default is 0 meaning
                exact match.
        """
        self._db = db
        self._distance_cutoff = distance_cutoff

    def solve(self, xword):
        '''Graph-based search for partial solutions to a crossword

        This implementation creates a graph describing possible words to play
        on the puzzle, nodes being words and the place to play them, and edges
        connecting words that can be played together without conflicts.

        Arguments:
            xword - a Crossword to be solved

        Yields:
            sorted list of tuples (Crossword, prob) of partially solved 
            Crosswords in order from most- to least-solved with prob=1.0 for
            each Crossword for now
        '''
        possible_answers = self.query_answers(xword)
        conflict_graph = build_conflict_graph(xword, possible_answers)

        for xwsolution in find_cliques(conflict_graph):
            solved = xword.copy()
            for fill in xwsolution:
                solved.set_fill(fill.clue, fill.answer)
            yield solved

    def query_answers(self, xword):
        '''From the self._db fetch all possible answers to all clues in xword

        DOES NOT currently use self._distance_cutoff, but this would be a good
        place for it - everything else would fall into place nicely if this
        method changed

        Arguments:
            xword - a Crossword

        Returns:
            dict(littleboxes.xword.XWClue: set(str))

        '''
        answers = {}

        for xwclue in xword.clues:
            db_answers = self._db.answers_for_clue_of_length(
                xwclue.text, len(xwclue.box_indices))

            if db_answers:
                answers[xwclue] = db_answers

        return answers
