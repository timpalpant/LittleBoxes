from littleboxes.solver.solver import Solver

class DictionarySolver(Solver):
    def __init__(self, dictionary):
        self.dictionary = dictionary

    def solve(self, xword, threshold=1.0):
        return xword
