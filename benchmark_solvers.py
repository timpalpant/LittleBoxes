import argparse
from concurrent import futures
import logging
import os

from littleboxes.cluedb import ClueDB
from littleboxes.dictionary import Dictionary, PhraseDictionary
from littleboxes.filter.nbest import nbest
from littleboxes.solver.solver import MultiStageSolver
from littleboxes.solver.cluedb_solver import ClueDBCliqueSolver
from littleboxes.solver.dictionary_solver import DictionaryCliqueSolver
from littleboxes.xword import Crossword

ROOT_DIR = os.path.dirname(os.path.realpath(__file__))
DATA_DIR = os.path.join(ROOT_DIR, 'data')
DICTIONARIES_DIR = os.path.join(DATA_DIR, 'dictionaries')
CLUES_DIR = os.path.join(DATA_DIR, 'clues')


def opts():
    parser = argparse.ArgumentParser(description='Benchmark a Crossword solver')
    parser.add_argument('puzzle', nargs='+', type=argparse.FileType('r'),
                        help='The crossword puzzle(s) to solve, in *.puz format')
    parser.add_argument('--nsolutions', type=int, default=10,
                        help='Number of solutions each solver generates (default: %(default)s)')
    parser.add_argument('--empty-penalty', type=int, default=2,
                        help='Penalty for unset squares (default: %(default)s)')
    parser.add_argument('--incorrect-penalty', type=int, default=10,
                        help='Penalty for incorrect squares (default: %(default)s)')
    parser.add_argument('--dictionary', type=argparse.FileType('r'),
                        default=os.path.join(DICTIONARIES_DIR, 'en.txt'),
                        help='Dictionary of words to use (default: %(default)s)')
    parser.add_argument('--cluedb', type=argparse.FileType('r'),
                        default=os.path.join(CLUES_DIR, 'clues.mpk'),
                        help='Clue database to use (default: %(default)s)')
    parser.add_argument('--nthreads', type=int, default=8,
                        help='Number of worker threads (default: %(default)s)')
    parser.add_argument('--logging',
                        choices=('debug', 'info', 'warning',
                                 'error', 'critical'),
                        default='info', help='Logging level (default: %(default)s)')
    return parser


def score_solution(x, xgolden, empty_penalty, incorrect_penalty):
    score = 0
    for guess, actual in zip(x.solution, xgolden.solution):
        if guess is None:
            score += empty_penalty
        elif guess != actual:
            score += incorrect_penalty
    return score


def run_solver(solver, x, max_examined=10):
    solutions = solver.solve(x)
    return nbest(solutions, 1, max_examined)[0]


def main():
    args = opts().parse_args()
    logging.basicConfig(level=getattr(logging, args.logging.upper()))

    logging.info("Loading test crossword puzzles")
    xs = [Crossword.load(p, include_solution=True) for p in args.puzzle]
    xs_unsolved = [Crossword(x.width, x.height, x.clues) for x in xs]

    logging.info("Loading clue DB")
    db = ClueDB.deserialize(args.cluedb)

    logging.info("Loading dictionary")
    dictionary = Dictionary.load(args.dictionary)
    pd = PhraseDictionary(dictionary)

    solver1 = ClueDBCliqueSolver(db)
    solver2 = MultiStageSolver(
        solvers=[
            ClueDBCliqueSolver(db),
            DictionaryCliqueSolver(dictionary),
        ],
    )

    solvers_to_benchmark = [solver1, solver2]

    executor = futures.ThreadPoolExecutor(args.nthreads)
    for i, solver in enumerate(solvers_to_benchmark):
        logging.info("Benchmarking Solver #%d", i+1)
        solutions = executor.map(lambda x: run_solver(solver, x, args.nsolutions), xs_unsolved)
        scores = map(
            lambda x, xgolden:
                score_solution(x, xgolden, args.empty_penalty, args.incorrect_penalty),
            solutions)
        logging.info("Results: best = %f, worst = %f, average = %f",
                     min(scores), max(scores), sum(scores)/float(len(scores)))

if __name__ == "__main__":
    main()
