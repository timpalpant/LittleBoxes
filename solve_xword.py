#!/usr/bin/env python

import argparse
import logging
import os

from littleboxes.cluedb import ClueDB
from littleboxes.dictionary import Dictionary
from littleboxes.solver import (
    ClueDBSolver,
    DictionarySolver,
    MultiStageSolver,
    NGramSolver,
)
from littleboxes.xword import Crossword

ROOT_DIR = os.path.dirname(os.path.realpath(__file__))
DATA_DIR = os.path.join(ROOT_DIR, 'data')
DICTIONARIES_DIR = os.path.join(DATA_DIR, 'dictionaries')
CLUES_DIR = os.path.join(DATA_DIR, 'clues')

def pretty_print(x):
    for r in xrange(x.height):
        row = x.solution[r*x.width:(r+1)*x.width]
        row = [l if l else 'X' for l in row]
        print ''.join(row)

def opts():
    parser = argparse.ArgumentParser(description='Solve a crossword puzzle.')
    parser.add_argument('puzzle', type=argparse.FileType('r'),
        help='The crossword puzzle to solve, in *.puz format')
    parser.add_argument('--dictionary', type=argparse.FileType('r'),
        default=os.path.join(DICTIONARIES_DIR, 'en.txt'),
        help='Dictionary of words to use (default: %(default)s')
    parser.add_argument('--cluedb', type=argparse.FileType('r'),
        default=os.path.join(CLUES_DIR, 'clues.db'),
        help='Clue database to use (default: %(default)s')
    parser.add_argument('--logging',
        choices=('debug', 'info', 'warning', 'error', 'critical'),
        default='info', help='Logging level (default: %(default)s)')
    return parser

def main():
    args = opts().parse_args()
    logging.basicConfig(level=getattr(logging, args.logging.upper()))

    logging.info("Loading crossword puzzle")
    x = Crossword.load(args.puzzle)

    logging.info("Loading clue DB")
    db = ClueDB.load(args.cluedb)

    logging.info("Loading dictionary")
    dictionary = Dictionary.load(args.dictionary)

    logging.info("Solving puzzle")
    solver = MultiStageSolver(
        solvers=[
            ClueDBSolver(db),
            DictionarySolver(dictionary),
            NGramSolver(dictionary),
        ]
    )
    solution = solver.solve(x)
    pretty_print(solution)

if __name__ == "__main__":
    main()
