from collections import namedtuple
import enum
import logging
import puz


class InvalidCrosswordException(Exception):
    pass


@enum.unique
class XWDirection(str, enum.Enum):
    ACROSS = 'A'
    DOWN = 'D'


XWCoordinate = namedtuple('XWCoordinate', ['num', 'direction'])
# Represents an individual clue in a Crossword puzzle:
#    coord (XWCoordinate): The number and direction of this clue.
#    text (str): The clue text.
#    box_indices (list(int)): Indices into the location of the boxes
#        that this clue references. Indices are linear, row-major order.
#        For across clues, they should be sequential; for down clues
#        they will be offset by the width of the Crossword.
XWClue = namedtuple('XWClue', ['coord', 'text', 'box_indices'])
XWFill = namedtuple('XWFill', ['clue', 'word'])


class Crossword(object):
    '''A Crossword puzzle is a set of XWClues arranged on an WxH grid,
    and an associated fill of letters in that grid.
    '''
    black_square = object()
    logger = logging.getLogger('littleboxes.xword.Crossword')

    def __init__(self, width, height, clues, solution=None):
        self.width = width
        self.height = height
        self.clues = clues
        if solution is not None:
            self.solution = solution
        else:
            self.solution = [None for _ in range(width * height)]
            self._fill_black_squares()
        self._validate()

    @property
    def n_set(self):
        return sum(1 for box in self.solution if box is not None)

    def _fill_black_squares(self):
        '''Goes through the set of clues, and marks squares which are not
        involved in any clue (black squares in the puzzle). These squares
        should be considered "filled" and never touched.
        '''
        touched = [False for _ in self.solution]
        for clue in self.clues:
            for idx in clue.box_indices:
                touched[idx] = True
        for idx, t in enumerate(touched):
            if not t:
                self.solution[idx] = self.black_square

    def _validate(self):
        for clue in self.clues:
            for idx in clue.box_indices:
                if idx < 0 or idx >= len(self.solution):
                    raise InvalidCrosswordException("Invalid clue indices")
                if self.solution[idx] == self.black_square:
                    raise InvalidCrosswordException("Clue with black square?!")

    def copy(self):
        '''Return a copy of this Crossword. The clues are not copied since they
        are immutable, but the solution is.
        '''
        sol_copy = list(self.solution)
        return self.__class__(self.width, self.height, self.clues, sol_copy)

    @classmethod
    def load(cls, istream, include_solution=False):
        p = puz.load(istream.read())
        cn = p.clue_numbering()
        clues = []
        for clue in cn.across:
            coord = XWCoordinate(num=clue['num'], direction=XWDirection.ACROSS)
            indices = tuple(clue['cell'] + i for i in range(clue['len']))
            xwc = XWClue(coord, clue['clue'], indices)
            clues.append(xwc)
        for clue in cn.down:
            coord = XWCoordinate(num=clue['num'], direction=XWDirection.DOWN)
            indices = tuple(clue['cell'] + i * p.width for i in range(clue['len']))
            xwc = XWClue(coord, clue['clue'], indices)
            clues.append(xwc)
        solution = None
        if include_solution:
            solution = list(p.solution)
        return cls(p.width, p.height, tuple(clues), solution)

    def get_fill(self, clue):
        '''Returns the current fill for the given clue.
        Unfilled squares are indicated by None.

        Args:
            clue (XWClue): The clue to get the current fill for.

        Returns:
            list(char or None): The current fill for this clue.
        '''
        return [self.solution[idx] for idx in clue.box_indices]

    def set_fill(self, clue, answer):
        '''Fill in the letters for the given clue with the provided answer.

        Args:
            clue (XWClue): The clue we are filling in.
            answer (str or list(char)): The letters to fill in for this clue.

        Raises:
            ValueError if the provided answer is the wrong length for this clue
            InvalidCrosswordException if the provided answer conflicts with an
                existing letter that has already been set.
        '''
        if len(answer) != len(clue.box_indices):
            raise ValueError("Answer '%s' is not the right length "
                             "for %s (%d != %d)" % (
                                 answer, clue,
                                 len(answer), len(clue.box_indices)))
        if self.would_conflict(clue, answer):
            raise InvalidCrosswordException(
                "Cannot set %s to %s (currently %s)" % (
                    clue, answer, self.get_fill(clue)))
        for idx, letter in zip(clue.box_indices, answer):
            self.solution[idx] = letter

    def would_conflict(self, clue, answer):
        '''Return whether or not the proposed answer for this clue conflicts
        with any letters that have already been filled.
        '''
        if len(answer) != len(clue.box_indices):
            raise ValueError("Answer '%s' is not the right length "
                             "for %s (%d != %d)" % (
                                 answer, clue,
                                 len(answer), len(clue.box_indices)))
        for idx, letter in zip(clue.box_indices, answer):
            if self.solution[idx] is not None and self.solution[idx] != letter:
                return True
        return False
