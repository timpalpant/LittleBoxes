import copy
import itertools
import logging
import sys

from cluedb import ClueDB
from xword import Crossword

def max_fill(x, possibilities):
    """Return the largest self-consistent fill over the provided set of
    possibilities.
    """
    logging.info("Finding max fill over %d possibilities", len(possibilities))
    best = x
    for i, p in enumerate(itertools.permutations(possibilities)):
        if i > 1000:
            break
        xp = copy.deepcopy(x)
        for t, num, answer in p:
            if t == 'across':
                if not xp.would_conflict_across(num, answer):
                    xp.set_across(num, answer)
            else:
                if not xp.would_conflict_down(num, answer):
                    xp.set_down(num, answer)
        logging.debug("Solution sets %d squares", xp.n_set())
        if xp.n_set() > best.n_set():
            logging.info("New best! Solution sets %d squares", xp.n_set())
            best = xp
    return best

def initial_pass(x, db):
    # Clues that we think we have an answer in the DB for.
    possibilities = []
    for clue in x.across.itervalues():
        possible_answers = db.answers_for_clue_of_length(clue['clue'], clue['len'])
        for pa in possible_answers:
            possibilities.append(('across', clue['num'], pa))
            
    for clue in x.down.itervalues():
        possible_answers = db.answers_for_clue_of_length(clue['clue'], clue['len'])
        for pa in possible_answers:
            possibilities.append(('down', clue['num'], pa))
            
    return max_fill(x, possibilities)

def solve(x, db):
    solution = initial_pass(x, db)
    return solution
    
def pretty_print(x):
    for r in xrange(x.height):
        row = x.solution[r*x.width:(r+1)*x.width]
        row = [l if l else 'X' for l in row]
        print ''.join(row)

def main():
    logging.basicConfig(level=logging.INFO)
    
    puzzle_filename = sys.argv[1]
    logging.info("Loading puzzle: %s", puzzle_filename)
    x = Crossword.load(puzzle_filename)
    
    logging.info("Loading clue DB")
    db = ClueDB.load('data/clues')
    
    logging.info("Solving puzzle")
    solution = solve(x, db)
    pretty_print(solution)

if __name__ == "__main__":
    main()
