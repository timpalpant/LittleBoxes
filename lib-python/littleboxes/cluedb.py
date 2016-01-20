from collections import defaultdict
import logging

class Clue(object):
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
        year = line[28:32]
        source = line[33:36]
        text = line[37:].rstrip()
        return cls(text, answer, source, year, num)
        
    def __str__(self):
        return "%s: %s (%s, %s, %s)" % (
            self.text, self.answer, self.source, self.year, self.num)

class ClueDB(object):
    def __init__(self):
        # Map of clue -> map of answers -> number of occurrences of answer.
        self._clue_to_answers = defaultdict(lambda: defaultdict(int))
        self._answers_by_length = defaultdict(set)
        
    @property
    def n_answers(self):
        return sum(sum(answer_to_counts.itervalues())
            for answer_to_counts in self._clue_to_answers.itervalues())
        
    @classmethod
    def load(cls, istream):
        db = cls()
        
        for line in istream:
            try:
                clue = Clue.parse(line)
                db.add_clue(clue.text, clue.answer)
            except Exception:
                logging.exception("Invalid entry: %s", line.rstrip())

        return db
        
    def add_clue(self, clue, answer):
        clue = self._normalize_clue(clue)
        answer = self._normalize_answer(answer)
        self._clue_to_answers[clue][answer] += 1
        self._answers_by_length[len(answer)].add(answer)
        
    def answers_for_clue(self, clue):
        clue = self._normalize_clue(clue)
        if clue in self._clue_to_answers:
            return self._clue_to_answers[clue]
        return {}
        
    def answers_of_length(self, n_letters):
        if n_letters in self._answers_by_length:
            return self._answers_by_length[n_letters]
        return set()
        
    def answers_for_clue_of_length(self, clue, n_letters):
        return set(answer for answer in self.answers_for_clue(clue).iterkeys()
                   if len(answer) == n_letters)
        
    def _normalize_clue(self, clue):
        return clue.lower()
        
    def _normalize_answer(self, answer):
        return answer.upper()
        
    def __len__(self):
        return len(self._clue_to_answers)
