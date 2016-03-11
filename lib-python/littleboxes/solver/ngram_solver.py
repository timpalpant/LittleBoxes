from littleboxes.solver.solver import Solver


class NGramSolver(Solver):
    """Solver that learns N-grams over letters from the provided dictionary,
    and uses them to find the most probable fill for empty squares in the puzzle.
    """

    def __init__(self, dictionary, n=2):
        self._dictionary = dictionary
        self.n = n

    def solve(self, xword):
        yield (xword, 1.0)
