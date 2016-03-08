'''
Created on Feb 24, 2016

@author: justinpalpant
'''
import unittest
import os
from cStringIO import StringIO
import time

from littleboxes.cluedb import ClueDB


PERFORMANCE = bool(int(os.getenv('PERFORMANCE', False)))


class TestSerialization(unittest.TestCase):
    TEST_DB = os.path.join(os.path.dirname(__file__),
                           'fixtures', 'test.cluedb')
    TEST_MPACK = os.path.join(os.path.dirname(__file__),
                              'fixtures', 'test.mpk')

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
            with open(self.TEST_DB, 'r') as db:
                start = time.time()
                test_db = ClueDB.load(db)
                self.times.append(time.time() - start)

    @unittest.skipIf(not PERFORMANCE, 'Not running performance tests')
    def test_speed_msgpack(self):
        self.testname = 'MessagePack'
        for _ in xrange(self.repeat):
            with open(self.TEST_MPACK, 'r') as dbdump:
                start = time.time()
                test_db = ClueDB.deserialize(dbdump)
                self.times.append(time.time() - start)

    def test_equality_msgpack(self):
        self.testname = 'MessagePack equality'
        start = time.time()

        with open(self.TEST_DB, 'r') as db:
            self.db = ClueDB.load(db)

        ostream = StringIO()
        self.db.serialize(ostream)
        istream = StringIO(ostream.getvalue())
        test_db = ClueDB.deserialize(istream)

        self.times.append(time.time() - start)

        self.assertEqual(self.db, test_db)

if __name__ == "__main__":
    logging.getLogger('root').disabled = True
    unittest.main()
