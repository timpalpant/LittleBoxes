from littleboxes.solver.solver import Solver
from littleboxes.xword import InvalidCrosswordException

from collections import namedtuple
import logging
from networkx import Graph, find_cliques
import time
import heapq


class XWFill(namedtuple("XWFill", ["clue", "word"])):
    __slots__ = ()

    def __str__(self):
        return '{0}{1}: {2}'.format(self.clue.coord.num, self.clue.coord.direction.value, self.word)


class ClueDBSolver(Solver):
    """Solver that looks for clue matches in the provided database."""

    logger = logging.getLogger('littleboxes.solver.ClueDBSolver')

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

        Returns:
            sorted list of tuples (Crossword, prob) of partially solved 
            Crosswords in order from most- to least-solved with prob=1.0 for
            each Crossword for now
        '''
        start_solutions = time.time()

        possible_answers = self.query_answers(xword)

        start_conflicts = time.time()
        conflict_graph = self.build_conflict_graph(xword, possible_answers)
        self.logger.info('Conflicts graph with {1} nodes and {2} edges built '
                         'in {0} seconds'.format(
                             time.time() - start_conflicts,
                             len(conflict_graph), conflict_graph.size()))

        start_cliques = time.time()
        cliques = find_cliques(conflict_graph)

        self.logger.info(
            'Maximal cliques found in {0} seconds'.format(time.time() - start_cliques))

        solutions = []
        for xwsolution in cliques:
            solved = xword.copy()
            for fill in xwsolution:
                solved.set_fill(fill.clue, fill.word)

            heapq.heappush(solutions, (len(xwsolution), solved, 1.0))

        self.logger.info('{0} solutions built in {1} seconds total'.format(
            len(solutions), time.time() - start_solutions))

        return [(sol, p) for (_, sol, p) in reversed(solutions)]

    def build_conflict_graph(self, xword, possible_answers):
        '''Build a network describing non-conflicting answer choices

        Arguments:
            xword - a Crossword object
            possible_answers - a dictionary as returned from self.query_answers
                e.g. {XWClue: set(str)}

        Returns:
            NetworkX Graph where nodes are (XWClue, str) pairs with the string
            being a possible solution to the clue.  Edges connect nodes which
            could be played simultaneously without conflict (no self-edges).
        '''
        g = Graph()

        for xwclue, wordset in possible_answers.iteritems():
            for word in wordset:
                if not xword.would_conflict(xwclue, word):
                    g.add_node(XWFill(clue=xwclue, word=word))

        for n in g:
            testcopy = xword.copy()
            testcopy.set_fill(n.clue, n.word)

            for other_n in g:
                if n.clue.coord == other_n.clue.coord:
                    continue

                if n.clue.coord.direction == other_n.clue.coord.direction:
                    g.add_edge(n, other_n)

                if not testcopy.would_conflict(other_n.clue, other_n.word):
                    g.add_edge(n, other_n)

        return g

    def apply_fill(self, xword, fill):
        '''Attempt to play the provided fill on a crossword

        Arguments:
            xword - a Crossword object
            fill - an iterable of XWFill tuples

        Returns:
            A new crossword object (the original remains unmodified) with the
            fill played on the crossword

        Raises:
            littleboxes.xword.InvalidCrosswordException if the fill cannot
                legally be played (either there is a conflict, or it would
                involve playing a word that has already been played)
            ValueError if the fill cannot be played because the word is longer
                than the clue calls for
        '''

        return new_xword

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
