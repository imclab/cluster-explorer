import os

from django.test import TestCase
from django.db import connection, transaction

from ingestion import *
from phrases import PhraseSequencer
from parser import parse
from sql_utils import execute_file


class DBTestCase(TestCase):
    
    def setUp(self):
        self.cursor = connection.cursor()
        execute_file(self.cursor, os.path.join(os.path.dirname(__file__), 'tables.sql'))
        
        self.cursor.execute("INSERT INTO corpora VALUES (1)")
        self.corpus_id = 1
        
    def tearDown(self):
        execute_file(self.cursor, os.path.join(os.path.dirname(__file__), 'drop_tables.sql'))
        

class TestSequencer(DBTestCase):
        
    def test_basic(self):
        s = PhraseSequencer(self.corpus_id)
        a = s.sequence('a')
        b = s.sequence('b')
        c = s.sequence('c')
        
        self.assertEqual(0, a)
        self.assertEqual(1, b)
        self.assertEqual(2, c)
        self.assertEqual(a, s.sequence('a'))
        self.assertEqual(b, s.sequence('b'))
        self.assertEqual(c, s.sequence('c'))
        
    def test_persistence(self):
        s1 = PhraseSequencer(self.corpus_id)
        a = s1.sequence('a')
        b = s1.sequence('b')
        c = s1.sequence('c')

        # new sequencer shouldn't see updates that haven't been persisted
        # note: should never do this in practice--should only ever be one
        # active sequencer per corpus.
        s2 = PhraseSequencer(self.corpus_id)
        self.assertEqual(0, s2.sequence('a'))
        
        s1.upload_new_phrases()
        self.assertEqual(1, s1.sequence('b')) # existing phrases still present
        self.assertEqual(3, s1.sequence('d')) # new phrases can still be added
        
        s3 = PhraseSequencer(self.corpus_id)
        self.assertEqual(2, s3.sequence('c')) # previously uploaded phrase appears
        self.assertEqual(3, s3.sequence('e')) # but not d=3, which wasn't uploaded
        
        s4 = PhraseSequencer(self.corpus_id + 1)
        self.assertEqual(0, s4.sequence('f'))  # sequencer with different corpus doesn't show at all


class TestParser(DBTestCase):
    
    def test_basic(self):
        t1 = "This is a basic text. Two sentences. Maybe three?"
        t2 = "Two sentences. Maybe...three? this is a basic text."
        s = PhraseSequencer(0)
        
        p1 = parse(t1, s)
        p2 = parse(t2, s)
        
        self.assertEqual([0, 1, 2], p1)
        self.assertEqual([0, 1, 2], p2)
       
        
class TestDocumentIngester(DBTestCase):
    
    def test_ingester(self):
        i = DocumentIngester(self.corpus_id)
        s = PhraseSequencer(self.corpus_id)
        
        t1 = 'This document has three sentences. One of which matches. Two of which do not.'
        t2 = 'This document has only two sentences. One of which matches.'
        
        i.record(t1, parse(t1, s))
        i.record(t2, parse(t2, s))
        
        s.upload_new_phrases()
        i.upload_new_documents()
        
        c = connection.cursor()
        
        c.execute("select count(*) from documents")
        self.assertEqual(2, c.fetchone()[0])
        
        c.execute("select count(*) from phrase_occurrences")
        self.assertEqual(5, c.fetchone()[0])

        # make sure we can add on to existing data
        i = DocumentIngester(self.corpus_id)
        s = PhraseSequencer(self.corpus_id)
        
        t3 = 'This document has only two sentences. Only one of which is new.'
        p3 = parse(t3, s)
        
        doc_id = i.record(t3, p3)
        self.assertEqual(2, doc_id)
        self.assertEqual([3, 4], p3)
        
        s.upload_new_phrases()
        i.upload_new_documents()
        
        c.execute("select count(*) from documents")
        self.assertEqual(3, c.fetchone()[0])
        
        c.execute("select count(*) from phrase_occurrences")
        self.assertEqual(7, c.fetchone()[0])
        
    def test_queries(self):
        self.test_ingester()
        
        c = connection.cursor()
        c.execute("""
            select document_id, array_agg(phrase_id)
            from (
                select document_id, phrase_id
                from phrase_occurrences
                where
                    corpus_id = %s
                order by document_id, phrase_id) x
            group by document_id
            order by document_id
        """, [self.corpus_id])
        
        self.assertEqual([(0, [0, 1, 2]), (1, [1, 3]), (2, [3, 4])], c.fetchall())

    def test_similarities(self):
        
        self.test_ingester()
        
        compute_similarities(self.corpus_id, [0, 1, 2])
        
        c = connection.cursor()
        
        c.execute("select count(*) from similarities")
        self.assertEqual(3, c.fetchone()[0])
        
        self.assertEqual(0.25, self.get_sim(c, 0, 1))
        self.assertEqual(0, self.get_sim(c, 0, 2))
        self.assertAlmostEqual(1.0/3, self.get_sim(c, 1, 2), places=5)
        
    def test_complete(self):
        ingest_documents(self.corpus_id, [
            'This document has three sentences. One of which matches. Two of which do not.',
            'This document has only two sentences. One of which matches.',
            'This document has only two sentences. Only one of which is new.'
        ])

        c = connection.cursor()
    
        c.execute("select count(*) from similarities")
        self.assertEqual(3, c.fetchone()[0])        
        self.assertEqual(0.25, self.get_sim(c, 0, 1))
        self.assertEqual(0, self.get_sim(c, 0, 2))
        self.assertAlmostEqual(1.0/3, self.get_sim(c, 1, 2), places=5)

        ingest_documents(self.corpus_id, [
            "This document matches nothing else.",
            "Only one of which is new."
        ])
 
        c.execute("select count(*) from similarities")
        self.assertEqual(10, c.fetchone()[0])        
        self.assertEqual(0, self.get_sim(c, 0, 3))
        self.assertEqual(0, self.get_sim(c, 0, 4))
        self.assertEqual(0, self.get_sim(c, 1, 3))
        self.assertEqual(0, self.get_sim(c, 1, 4))
        self.assertEqual(0, self.get_sim(c, 2, 3))
        self.assertAlmostEqual(0.5, self.get_sim(c, 2, 4))
        self.assertEqual(0, self.get_sim(c, 3, 4))


    def get_sim(self, c, x, y):
        c.execute("""
            select similarity
            from similarities
            where
                corpus_id = %s
                and low_document_id = %s
                and high_document_id = %s
        """, [self.corpus_id, min(x, y), max(x, y)])
        
        return c.fetchone()[0]


if __name__ == '__main__':
    unittest.main()