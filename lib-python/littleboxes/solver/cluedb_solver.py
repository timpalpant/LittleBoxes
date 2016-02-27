from littleboxes.solver.solver import Solver


class ClueDBSolver(Solver):
    """Solver that looks for clue matches in the provided database."""

    def __init__(self, db, distance_cutoff=0):
        """Args:
            db (ClueDB): The database of clues to search for answers.
            distance_cutoff (int): Clues will only be considered a match if they
                have Levenstein distance <= cutoff. Default is 0 meaning exact match.
        """
        self._db = db
        self._distance_cutoff = distance_cutoff

    def solve(self, xword):
        pass
