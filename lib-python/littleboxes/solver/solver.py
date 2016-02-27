from abc import ABCMeta, abstractmethod
import copy


class Solver(object):
    """Interface for a generic crossword solver."""
    __metaclass__ = ABCMeta

    @abstractmethod
    def solve(self, xword):
        """Attempt to solve the provided crossword puzzle.

        Args:
            xword (Crossword): The puzzle to solve.

        Returns:
            list((Crossword, float)): List of potential solutions of crossword puzzle,
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
        return self._solve_recursive(self.solvers, xword)

    def _solve_recursive(self, solvers, xword):
        """Applies the first solver to the puzzle. Takes all of its proposed solutions
        and passes them to the next solver. Continues until all solvers have been applied
        and then returns the set of all solutions.

        Args:
            solvers (list(Solver)): A sequence of solvers to apply to the puzzle.
            xword (Crossword): The crossword puzzle to solve.

        Returns;
            list((Crossword, float)): A list of possible solutions to the crossword,
                and their associated confidences (higher is better).
        """
        solver = solvers[0]
        partial_solutions = solver.solve(xword)
        if len(solvers) > 1:  # Pass solutions on to next solver.
            final_solutions = []
            for partial_solution, l1 in partial_solutions:
                for solution, l2 in self._solve_recursive(solvers[1:], partial_solution):
                    final_solutions.append((solution, l1 * l2))
        else:
            final_solutions = partial_solutions

        return final_solutions
