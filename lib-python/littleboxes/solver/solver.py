from abc import ABCMeta, abstractmethod
import copy


class Solver(object, metaclass=ABCMeta):
    """Interface for a generic crossword solver."""

    @abstractmethod
    def solve(self, xword):
        """Attempt to solve the provided crossword puzzle.

        Args:
            xword (Crossword): The puzzle to solve.

        Yields:
            (float, Crossword): Potential solutions of crossword puzzle,
                with some measure of confidence (higher is better).
        """
        pass


class MultiStageSolver(Solver):
    """Solver that strings a sequence of Solvers together."""

    def __init__(self, solvers):
        if not solvers:
            raise ValueError("You must provide at least 1 solver")
        self.solvers = solvers

    def solve(self, xword):
        """Apply each of the solvers to the given puzzle.
        All of the solutions returned at each stage are carried to the next round.
        The likelihood for the returned solutions is the product of the likelihood
        that was assigned by each solver.
        """
        for p, sol in self._solve_recursive(self.solvers, xword):
            yield p, sol

    def _solve_recursive(self, solvers, xword):
        """Applies the first solver to the puzzle. Takes all of its proposed solutions
        and passes them to the next solver. Continues until all solvers have been applied
        and then returns the set of all solutions.

        Args:
            solvers (list(Solver)): A sequence of solvers to apply to the puzzle.
            xword (Crossword): The crossword puzzle to solve.

        Yields:
            (float, Crossword): A possible Crossword solution and confidence/value.
        """
        solver = solvers[0]
        for p1, s1 in solver.solve(xword):
            if len(solvers) > 1:  # Pass solutions on to next solver.
                for p2, s2 in self._solve_recursive(solvers[1:], s1):
                    yield p1*p2, s2
            else:
                yield p1, s1
