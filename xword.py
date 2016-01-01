import logging
import puz

from cluedb import Clue

class InvalidCrosswordException(Exception):
    pass

class Crossword(object):
    BLACK_SQUARE = '.'
    
    def __init__(self, width, height, across, down, black_squares):
        self.width = width
        self.height = height
        self.across = {clue['num']: clue for clue in across}
        self.down = {clue['num']: clue for clue in down}
        self.solution = [None for i in xrange(width*height)]
        for bs in black_squares:
            self.solution[bs] = self.BLACK_SQUARE
        self._validate()
            
    @classmethod
    def load(self, filename):
        with open(filename) as fd:
            p = puz.load(fd.read())
        cn = p.clue_numbering()
        black_squares = [i for i, c in enumerate(p.fill)
                         if c == self.BLACK_SQUARE]
        return self(p.width, p.height, cn.across, cn.down, black_squares)
            
    def _validate(self):
        for clue in self.across.itervalues():
            squares = self.get_across(clue['num'])
            if any(s == self.BLACK_SQUARE for s in squares):
                raise InvalidCrosswordException(
                    "%d-across contains a black square?! (%s: %s): %s" % (
                        clue['num'], clue, squares, self.solution))
        for clue in self.down.itervalues():
            squares = self.get_down(clue['num'])
            if any(s == self.BLACK_SQUARE for s in squares):
                raise InvalidCrosswordException(
                    "%d-down contains a black square?! (%s: %s): %s" % (
                        clue['num'], clue, squares, self.solution))
            
    def row(self, i):
        return i / self.width
        
    def col(self, i):
        return i % self.width
        
    def index(self, row, col):
        return row*self.width + col
        
    def is_set(self, row, col):
        i = self.index(row, col)
        return (self.solution[i] is not None)
        
    def n_set(self):
        return sum(l is not None for l in self.solution)
        
    def would_conflict_across(self, num, answer):
        if num not in self.across:
            raise ValueError("No such clue %d-across" % num)
        if len(answer) != self.across[num]['len']:
            raise ValueError("Answer '%s' is not the right length "
                "for %d-across (%d != %d)" % (
                    answer, num, len(answer), self.across[num]['len']))
        i = self.across[num]['cell']
        for j, letter in enumerate(answer):
            cur = self.solution[i+j]
            if cur is not None and cur != letter:
                return True
        return False
        
    def get_across(self, num):
        if num not in self.across:
            raise ValueError("No such clue %d-across" % num)
        i = self.across[num]['cell']
        l = self.across[num]['len']
        return [self.solution[i+j] for j in xrange(l)]
        
    def set_across(self, num, answer):
        if num not in self.across:
            raise ValueError("No such clue %d-across" % num)
        if len(answer) != self.across[num]['len']:
            raise ValueError("Answer '%s' is not the right length "
                "for %d-across (%d != %d)" % (
                    answer, num, len(answer), self.across[num]['len']))
        logging.debug("Setting %d-across (%s) = %s",
            num, self.across[num]['clue'], answer)
        i = self.across[num]['cell']
        for j, letter in enumerate(answer):
            self.solution[i+j] = letter

    def would_conflict_down(self, num, answer):
        if num not in self.down:
            raise ValueError("No such clue %d-down" % num)
        if len(answer) != self.down[num]['len']:
            raise ValueError("Answer '%s' is not the right length "
                "for %d-down (%d != %d)" % (
                    answer, num, len(answer), self.down[num]['len']))
        i = self.down[num]['cell']
        for j, letter in enumerate(answer):
            cur = self.solution[i+j*self.width]
            if cur is not None and cur != letter:
                return True
        return False
            
    def get_down(self, num):
        if num not in self.down:
            raise ValueError("No such clue %d-down" % num)
        i = self.down[num]['cell']
        l = self.down[num]['len']
        return [self.solution[i+j*self.width] for j in xrange(l)]
            
    def set_down(self, num, answer):
        if num not in self.down:
            raise ValueError("No such clue %d-down" % num)
        if len(answer) != self.down[num]['len']:
            raise ValueError("Answer '%s' is not the right length "
                "for %d-down (%d != %d)" % (
                    answer, num, len(answer), self.down[num]['len']))
        logging.debug("Setting %d-down (%s) = %s",
            num, self.down[num]['clue'], answer)
        i = self.down[num]['cell']
        for j, letter in enumerate(answer):
            self.solution[i+j*self.width] = letter
