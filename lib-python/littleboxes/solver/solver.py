from abc import ABCMeta, abstractmethod
import copy

class Solver(object):
    """Interface for a generic crossword solver."""
    __metaclass__ = ABCMeta

    @abstractmethod
    def solve(self, xword, threshold=1.0):
        """Attempt to solve the provided crossword puzzle.

        Args:
            xword (Crossword): The puzzle to solve.
            threshold (float): How hard to try to find a solution (0.0-1.0).
                If threshold == 1.0, then all squares must be filled,
                regardless of uncertainty.

        Returns:
            Crossword: solved crossword puzzle.
        """
        pass

class MultiStageSolver(Solver):
    """Solver that strings a sequence of Solvers together."""
    def __init__(self, solvers):
        self.solvers = solvers

    def solve(self, xword, threshold=1.0):
        x = copy.deepcopy(xword)
        for solver, threshold in self.solvers:
            x = solver.solve(x, threshold)
        return x
