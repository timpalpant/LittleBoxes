'''
Created on Feb 24, 2016

@author: justinpalpant
'''
import unittest
import os
import time

from littleboxes.cluedb import ClueDB

ROOT_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', '..')
DATA_DIR = os.path.join(ROOT_DIR, 'data')
DICTIONARIES_DIR = os.path.join(DATA_DIR, 'dictionaries')
CLUES_DIR = os.path.join(DATA_DIR, 'clues')

PERFORMANCE = False


class Test(unittest.TestCase):

    def setUp(self):
        self.repeat = 10
        self.times = []

    def tearDown(self):
        print 'Test: {0}'.format(self.testname)
        times = self.times
        print 'Mean loading time {0} seconds'.format(sum(times)/len(times))

    @unittest.skipIf(not PERFORMANCE, 'Not running performance tests')
    def test_speed_load(self):
        self.testname = 'Loading'
        for _ in xrange(self.repeat):
            with open(os.path.join(CLUES_DIR, 'clues.db'), 'r') as db:
                start = time.time()
                test_db = ClueDB.load(db)
                self.times.append(time.time() - start)

    @unittest.skipIf(not PERFORMANCE, 'Not running performance tests')
    def test_speed_msgpack(self):
        self.testname = 'MessagePack'
        for _ in xrange(self.repeat):
            with open(os.path.join(CLUES_DIR, 'clues_serial.mpk'), 'r') as dbdump:
                start = time.time()
                test_db = ClueDB.deserialize(dbdump)
                self.times.append(time.time() - start)

    def test_equality_msgpack(self):
        self.testname = 'MessagePack equality'
        start = time.time()

        with open(os.path.join(CLUES_DIR, 'clues.db'), 'r') as db:
            self.db = ClueDB.load(db)

        with open(os.path.join(CLUES_DIR, 'clues_serial.mpk'), 'w') as dbdump:
            self.db.serialize(dbdump)

        with open(os.path.join(CLUES_DIR, 'clues_serial.mpk'), 'r') as dbdump:
            test_db = ClueDB.deserialize(dbdump)

        self.times.append(time.time() - start)

        self.assertEqual(self.db, test_db)

if __name__ == "__main__":
    logging.getLogger('root').disabled = True
    unittest.main()
