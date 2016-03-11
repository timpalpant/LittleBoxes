'''
This script can be used to generate a ClueDB in *.mpk format
from a set of input *.puz files.
'''

import argparse
import glob
import logging

from littleboxes.cluedb import ClueDB
from littleboxes.xword import Crossword


def opts():
    parser = argparse.ArgumentParser(description='Generate a ClueDB from *.puz files')
    parser.add_argument('pattern', nargs='+',
                        help='Pattern for *.puz files to include in ClueDB')
    parser.add_argument('--output', required=True,
                        help='Output ClueDB file, in *.mpk format')
    parser.add_argument('--logging',
                        choices=('debug', 'info', 'warning',
                                 'error', 'critical'),
                        default='info', help='Logging level (default: %(default)s)')
    return parser


def main():
    args = opts().parse_args()
    logging.basicConfig(level=getattr(logging, args.logging.upper()))

    db = ClueDB()

    logging.info("Loading puzzles into the ClueDB")
    for pattern in args.pattern:
        logging.info("Finding files matching pattern: %s", pattern)
        for puz in glob.iglob(pattern):
            logging.debug("Processing: %s", puz)
            try:
                with open(puz) as fd:
                    x = Crossword.load(fd, include_solution=True)
                    for clue in x.clues:
                        word = ''.join(x.get_fill(clue))
                        db.add(clue.text, word)
            except Exception:
                logging.exception("Error loading: %s", puz)

    logging.info("Saving ClueDB to %s", args.output)
    with open(args.output, 'w') as fd:
        db.serialize(fd)

if __name__ == "__main__":
    main()
