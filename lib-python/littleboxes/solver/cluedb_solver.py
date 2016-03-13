import logging

from littleboxes.solver.clique import (
    CliqueSolver,
)


class ClueDBCliqueSolver(CliqueSolver):
    """Solver that looks for clue matches in the provided database."""

    logger = logging.getLogger('littleboxes.solver.ClueDBCliqueSolver')

    def __init__(self, db, clue_threshold=1.0):
        """Args:
            db (ClueDB): The database of clues to search for answers.
            clue_threshold (float, 0.0-1.0): Clues will be considered a match if
                they have this much N-gram similarity.
        """
        self._db = db
        self._clue_threshold = clue_threshold

    def query_answers(self, xword):
        '''From the self._db fetch all possible answers to all clues in xword

        Arguments:
            xword - a Crossword

        Returns:
            dict(littleboxes.xword.XWClue: set(str))

        '''
        answers = {}

        for xwclue in xword.clues:
            all_answers = set()
            self.logger.debug('Finding clues within %f of %r', self._clue_threshold, xwclue.text)
            for clue, similarity in self._db.search(xwclue.text, self._clue_threshold):
                self.logger.debug('Found clue %r (similarity = %f)', clue, similarity)
                db_answers = self._db.answers(clue, len(xwclue.box_indices))
                self.logger.debug('%d possible answers for %r', len(db_answers), clue)
                all_answers.update(db_answers)
            if all_answers:
                self.logger.debug('Found %d possible answers for %s', len(all_answers), xwclue)
                answers[xwclue] = all_answers

        n_answers = sum(len(fills) for fills in answers.itervalues())
        self.logger.debug('%d possible answers for all clues', n_answers)
        return answers
