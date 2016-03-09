import logging
import msgpack
from ngram import NGram


class ClueDBRecord(object):

    def __init__(self, text, answer, source=None, year=None, num=None):
        self.text = text
        self.answer = answer
        self.source = source
        self.year = year
        self.num = num

    @classmethod
    def parse(cls, line):
        answer = line[:26].rstrip()
        num = int(line[26])
        try:
            year = int(line[28:32])
        except ValueError:
            year = -1
        source = line[33:36]
        text = line[37:].rstrip()
        return cls(text, answer, source, year, num)

    def __str__(self):
        return "%s: %s (%s, %s, %s)" % (
            self.text, self.answer, self.source, self.year, self.num)


class ClueDB(object):
    logger = logging.getLogger('littleboxes.xword.ClueDB')

    def __init__(self):
        # Map of clue -> set of answers that have been used for that clue.
        self._clue_to_answers = {}
        self._fuzzy_clueset = NGram()

    @classmethod
    def load(cls, istream, source=None, year_range=None):
        """Load clue database from the provided iterable over Clue lines.

        Args:
            istream (iterable(str)): Iterable over Clue lines.
            source (str or None): If provided, only load clues from this source.
            year_range (tuple(int, int)): If provided, only load clues from this range of years.

        Returns:
            ClueDB
        """
        db = cls()

        for line in istream:
            try:
                clue = ClueDBRecord.parse(line)
                if source and clue.source != source:
                    continue
                if year_range and not (year_range[0] <= clue.year <= year_range[1]):
                    continue
                db.add(clue.text, clue.answer)
            except Exception:
                cls.logger.exception("Invalid entry: %s", line.rstrip())

        return db

    @classmethod
    def deserialize(cls, file_object):
        """Deserialize a saved ClueDB

        Arguments:
            file_object: a file_like object supporting the .read() method

        Returns:
            ClueDB
        """

        db = cls()
        db._clue_to_answers = msgpack.load(file_object)
        for clue in db._clue_to_answers:
            db._fuzzy_clueset.add(clue)
        return db

    def serialize(self, file_object):
        """Serialize the ClueDB instance to a file using MessagePack

        Arguments:
            file_object: a file-like object that supports the .write(str) method

        Returns:
            Nothing
        """
        msgpack.dump(self._clue_to_answers, file_object)

    def add(self, clue, answer):
        '''Add a clue-answer pair to the DB.'''
        clue = self._normalize_clue(clue)
        answer = self._normalize_answer(answer)
        if clue not in self._clue_to_answers:
            self._clue_to_answers[clue] = set()
        self._clue_to_answers[clue].add(answer)
        self._fuzzy_clueset.add(clue)

    def search(self, clue, threshold=1.0):
        '''Search the DB for clues similar to @clue.

        Args:
            clue (str): The search string.
            threshold (float, 0.0-1.0): Fraction of similar N-grams
                in clue required for match.

        Returns:
            list(tuple(str, float)): Matching clues and their similarity,
                in descending order from most similar.
        '''
        clue = self._normalize_clue(clue)
        return self._fuzzy_clueset.search(clue, threshold=threshold)

    def answers(self, clue):
        '''Get previous answers for @clue.'''
        clue = self._normalize_clue(clue)
        return self._clue_to_answers[clue]

    def _normalize_clue(self, clue):
        return clue.lower()

    def _normalize_answer(self, answer):
        return answer.upper()

    def __len__(self):
        return len(self._clue_to_answers)

    def __eq__(self, other):
        return (self._clue_to_answers == other._clue_to_answers)
