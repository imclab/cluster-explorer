
import unittest

from ngrams import Sequencer, NGramSpace, overlap, jaccard
from clustering import Clustering, SymmetricMatrix


# for use in interactive tests
test_docs = [
    "Penguins swim in the waters of antarctica.",
    "In antarctica, penguins swim in the waters.",
    "The waters where penguins swim are in antarctica.",
    
    "Bears eat honey in the forest.",
    "The forest where bears eat has honey.",
    "Honey is eaten bears in the forest.",
    
    "Sea gulls fly on the coast.",
    "Sea gulls fly over the water.",
]



class TestSymmetricMatrix(unittest.TestCase):
    
    def test_basic(self):
        m = SymmetricMatrix(5)
        
        self.assertEqual(5, len(m))
        
        self.assertEqual(0, m[2,3])
        
        m[2,3] = 2.3
        
        self.assertEqual(2.3, m[2, 3])
        self.assertEqual(2.3, m[3, 2])
    
    def test_translate(self):
        m = SymmetricMatrix(5)
        
        for i in range(0, 5):
            for j in range(0, i + 1):
                m[i, j] = i + j * 0.1
        
        self.assertEqual(2.1, m[1,2])
        self.assertEqual(2.1, m[2,1])
        
        s = m.submatrix([0, 3, 4])
        
        self.assertEqual(3, len(s))
        
        self.assertEqual(0.0, s[0,0])
        self.assertEqual(3.3, s[1,1])
        self.assertEqual(4.4, s[2,2])
        
        self.assertEqual(4.3, s[1, 2])
        self.assertEqual(4.3, s[2, 1])        
        


class TestSequencer(unittest.TestCase):
    
    def test_basic(self):
        s = Sequencer()
        a = s.id('a')
        b = s.id('b')
        c = s.id('c')
        
        self.assertEqual(1, a)
        self.assertEqual(2, b)
        self.assertEqual(3, c)
        self.assertEqual(a, s.id('a'))
        self.assertEqual(b, s.id('b'))
        self.assertEqual(c, s.id('c'))
        
    def test_ngram(self):
        s = Sequencer()
        
        abc = s.id(('a', 'b', 'c'))
        bcd = s.id(('b', 'c', 'd'))
        
        self.assertEqual(1, abc)
        self.assertEqual(2, bcd)
        self.assertEqual(abc, s.id(('a', 'b', 'c')))
        self.assertEqual(bcd, s.id(('b', 'c', 'd')))


class TestNGramSpace(unittest.TestCase):
    
    def test_unigram(self):
        unigrams = NGramSpace(1)
        
        x = unigrams.parse('This is a sentence')
        y = unigrams.parse('This is another sentence')
        
        self.assertEqual([1, 2, 3, 4], x)
        self.assertEqual([1, 2, 4, 5], y)
        
        self.assertEqual(3, overlap(x, y))
        self.assertEqual(3, overlap(y, x))
        
        self.assertEqual(3.0/5.0, jaccard(x, y))
        self.assertEqual(3.0/5.0, jaccard(y, x))
   
    def test_bigram(self):
        unigrams = NGramSpace(2)

        x = unigrams.parse('This is a sentence')
        y = unigrams.parse('This is another sentence')

        self.assertEqual([1, 2, 3], x)
        self.assertEqual([1, 4, 5], y)

        self.assertEqual(1, overlap(x, y))
        self.assertEqual(1, overlap(y, x))
        
        self.assertEqual(1.0/5.0, jaccard(x, y))
        self.assertEqual(1.0/5.0, jaccard(y, x))

    def test_trigram(self):
        unigrams = NGramSpace(3)

        x = unigrams.parse('This is a sentence')
        y = unigrams.parse('This is another sentence')

        self.assertEqual([1, 2], x)
        self.assertEqual([3, 4], y)

        self.assertEqual(0, overlap(x, y))
        self.assertEqual(0, overlap(y, x))
        
        self.assertEqual(0, jaccard(x, y))
        self.assertEqual(0, jaccard(y, x))     

class TestClustering(unittest.TestCase):
    
    def test_distance(self):
        raw_docs = ['a b c', 'b c d', 'd e f']
        ngrams = NGramSpace(1)
        docs = [ngrams.parse(raw) for raw in raw_docs]
        
        c = Clustering(docs)
        
        self.assertEqual(0, c.distance[0, 0])
        self.assertEqual(0.5, c.distance[1, 0])
        self.assertEqual(0, c.distance[1, 1])
        self.assertEqual(1.0, c.distance[2, 0])
        self.assertEqual(0.8, c.distance[2, 1])
        self.assertEqual(0, c.distance[2, 2])
        
    def test_clustering(self):
        raw_docs = ['a b c', 'b c d', 'd e f']
        ngrams = NGramSpace(1)
        docs = [ngrams.parse(raw) for raw in raw_docs]
        
        c = Clustering(docs)
        
        self.assertEqual((1, 0), c.min_link())
        
        c.merge(1, 0)
        self.assertEqual([1, 1, 2], c.assignments)
        
        self.assertEqual((2, 1), c.min_link())

        c.merge(2, 0)
        self.assertEqual([2, 2, 2], c.assignments)
    
    def test_pairs(self):
        ngrams = NGramSpace(1)
        docs = [ngrams.parse(raw) for raw in test_docs]
        c = Clustering(docs)
        
        self.assertEqual((1, 0), c.closest_pair([0, 1, 2]))
        self.assertEqual((5, 3), c.closest_pair([3, 4, 5]))
        self.assertEqual((7, 6), c.closest_pair([6, 7]))
        
        self.assertEqual((2, 0), c.farthest_pair([0, 1, 2]))
        self.assertEqual((5, 4), c.farthest_pair([3, 4, 5]))
        self.assertEqual((7, 6), c.farthest_pair([6, 7]))        
        
        
if __name__ == '__main__':
    unittest.main()