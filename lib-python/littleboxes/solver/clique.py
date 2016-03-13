from abc import abstractmethod
import bisect
from collections import defaultdict
import logging

from littleboxes.solver.solver import Solver
from littleboxes.xword import XWFill, pretty_print


class CliqueSolver(Solver):
    '''Abstract base class for clique-based solvers.
    Subclasses must provide query_answers(Crossword).
    '''
    logger = logging.getLogger('littleboxes.solver.clique.CliqueSolver')

    @abstractmethod
    def query_answers(self, xword):
        '''Return possible answers to all clues in xword.

        Arguments:
            xword - a Crossword

        Returns:
            dict(littleboxes.xword.XWClue: set(str))

        '''
        raise NotImplementedError

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
        self.logger.info('Getting set of potential answers')
        potential_answers = self.query_answers(xword)
        self.logger.info('Generating conflict graph')
        g = XWFillGraph(xword, potential_answers)

        self.logger.info('Finding cliques in conflict graph')
        n = 0
        for clique in find_cliques(g):
            solved = xword.copy()
            for node_id in clique:
                fill = g.id2fill(node_id)
                self.logger.info('Filling "%s" with %r', fill.clue, fill.word)
                solved.set_fill(fill.clue, fill.word)
            self.logger.info('Found solution')
            pretty_print(solved)
            yield solved.n_set, solved
            n += 1
        self.logger.info('Generated %d possible solutions', n)


class XWFillGraph(object):
    '''Represents a graph of XWFill nodes.

    Neighbors (compatible fills) can be retrieved with __getitem__,
    and are generated on-the-fly to avoid needing to store the entire
    adjacency graph in memory.
    '''
    logger = logging.getLogger('littleboxes.solver.clique.XWFillGraph')

    def __init__(self, xword, possible_answers):
        self._xword = xword
        self._id2node = []
        self._clue2ids = {}
        self._init_tables(possible_answers)
        self._id2conflicts = []
        self._init_conflicts()

    def _init_tables(self, possible_answers):
        for xwclue, wordset in possible_answers.iteritems():
            clue_ids = set()
            for word in wordset:
                node = XWFill(clue=xwclue, word=word)
                id = len(self._id2node)
                self._id2node.append(node)
                clue_ids.add(id)
            self._clue2ids[xwclue] = clue_ids
        self.logger.debug('Graph has %d nodes', len(self._id2node))

    def _init_conflicts(self):
        for id in self:
            conflicts = self._get_incompatible(id)
            self._id2conflicts.append(conflicts)

    def keys(self):
        return range(len(self._id2node))

    def id2fill(self, id):
        return self._id2node[id]

    def __iter__(self):
        return iter(self.keys())

    def __getitem__(self, id):
        '''Return neighbors (compatible fills) of @id.'''
        return [i for i in self if i not in self._id2conflicts[id]]

    def _get_incompatible(self, id):
        self.logger.debug('Finding neighbors of node %s', id)
        # Nodes are incompatible if they:
        #   1. Are for the same clue, OR
        #   2. Cross and have conflicting letters for the shared box.
        n = self._id2node[id]
        conflicting = set(self._clue2ids[n.clue])
        n_other = len(conflicting)
        self.logger.debug('Excluding %d other answers for this clue',
                          n_other)
        for idx, box in enumerate(n.clue.box_indices):
            crossing_clue = self._xword.crossing(n.clue, box)
            if crossing_clue in self._clue2ids:
                other_idx = bisect.bisect_left(crossing_clue.box_indices, box)
                for other_id in self._clue2ids[crossing_clue]:
                    other_n = self._id2node[other_id]
                    if other_n.word[other_idx] != n.word[idx]:
                        conflicting.add(other_id)
        self.logger.debug('Excluding %d conflicting crossing answers',
                          len(conflicting)-n_other)
        return conflicting


def find_cliques(graph):
    '''Finds all maximal cliques in a graph using the Bron-Kerbosch
    algorithm. The input graph here is in the adjacency list format,
    a dict with vertexes as keys and lists of their neighbors as values.'''
    p = set(graph.keys())
    r = set()
    x = set()
    for v in degeneracy_ordering(graph):
        neighs = graph[v]
        for clique in find_cliques_pivot(graph, r.union([v]),
                                         p.intersection(neighs),
                                         x.intersection(neighs)):
            yield clique
        p.remove(v)
        x.add(v)


def find_cliques_pivot(graph, r, p, x):
    if len(p) == 0 and len(x) == 0:
        yield r
    else:
        u = iter(p.union(x)).next()
        for v in p.difference(graph[u]):
            neighs = graph[v]
            for clique in find_cliques_pivot(graph, r.union([v]),
                                             p.intersection(neighs),
                                             x.intersection(neighs)):
                yield clique
            p.remove(v)
            x.add(v)


def degeneracy_ordering(graph):
    ordering = []
    ordering_set = set()
    degrees = defaultdict(lambda: 0)
    degen = defaultdict(list)
    max_deg = -1
    for v in graph:
        deg = len(graph[v])
        degen[deg].append(v)
        degrees[v] = deg
        if deg > max_deg:
            max_deg = deg

    while True:
        i = 0
        while i <= max_deg:
            if len(degen[i]) != 0:
                break
            i += 1
        else:
            break
        v = degen[i].pop()
        ordering.append(v)
        ordering_set.add(v)
        for w in graph[v]:
            if w not in ordering_set:
                deg = degrees[w]
                degen[deg].remove(w)
                if deg > 0:
                    degrees[w] -= 1
                    degen[deg - 1].append(w)

    ordering.reverse()
    return ordering
