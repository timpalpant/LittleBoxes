from littleboxes.solver.solver import Solver

class DictionarySolver(Solver):
    """Solver that looks for words in the provided dictionary that
    satisfy the current constraints in the puzzle.
    """
    def __init__(self, dictionary):
        """Args:
            dictionary (Dictionary): Dictionary of words to use as potential fills.
        """
        self._dictionary = dictionary

    def solve(self, xword):
        return xword
