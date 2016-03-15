import argparse
import logging
import os

from littleboxes.cluedb import ClueDB
from littleboxes.dictionary import Dictionary, PhraseDictionary
from littleboxes.solver.solver import MultiStageSolver
from littleboxes.solver.cluedb_solver import ClueDBCliqueSolver
from littleboxes.solver.dictionary_solver import (
    DictionaryAnnealSolver,
    DictionaryCliqueSolver,
    DictionaryGuessSolver,
)
from littleboxes.xword import Crossword

ROOT_DIR = os.path.dirname(os.path.realpath(__file__))
DATA_DIR = os.path.join(ROOT_DIR, 'data')
DICTIONARIES_DIR = os.path.join(DATA_DIR, 'dictionaries')
CLUES_DIR = os.path.join(DATA_DIR, 'clues')


def pretty_print(x):
    for r in xrange(x.height):
        row = []
        for letter in x.solution[r * x.width:(r + 1) * x.width]:
            if letter is None:
                row.append('~')
            elif letter == Crossword.black_square:
                row.append('*')
            else:
                row.append(letter)
        print ''.join(row)


def opts():
    parser = argparse.ArgumentParser(description='Solve a crossword puzzle.')
    parser.add_argument('puzzle', type=argparse.FileType('r'),
                        help='The crossword puzzle to solve, in *.puz format')
    parser.add_argument('--dictionary', type=argparse.FileType('r'),
                        default=os.path.join(DICTIONARIES_DIR, 'en.txt'),
                        help='Dictionary of words to use (default: %(default)s)')
    parser.add_argument('--cluedb', type=argparse.FileType('r'),
                        default=os.path.join(CLUES_DIR, 'clues.mpk'),
                        help='Clue database to use (default: %(default)s)')
    parser.add_argument('--nsolutions', type=int, default=1,
                        help='Number of solutions to show (default: %(default)s)')
    parser.add_argument('--logging',
                        choices=('debug', 'info', 'warning',
                                 'error', 'critical'),
                        default='info', help='Logging level (default: %(default)s)')
    return parser


def main():
    args = opts().parse_args()
    logging.basicConfig(level=getattr(logging, args.logging.upper()))

    logging.info("Loading crossword puzzle")
    x = Crossword.load(args.puzzle)

    logging.info("Loading clue DB")
    db = ClueDB.deserialize(args.cluedb)

    logging.info("Loading dictionary")
    dictionary = Dictionary.load(args.dictionary)
    # TODO: Too many possibilities for clique-solving!
    pd = PhraseDictionary(dictionary)

    logging.info("Solving puzzle")
    solver = MultiStageSolver(
        solvers=[
            ClueDBCliqueSolver(db),
            DictionaryAnnealSolver(dictionary),
        ],
    )

    solutions = solver.solve(x)
    for i, (p, solution) in enumerate(solutions):
        logging.info("Solution #%d (p = %f)", i+1, p)
        pretty_print(solution)

if __name__ == "__main__":
    main()
