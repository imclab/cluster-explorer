


class Sequencer(object):
    
    def __init__(self):
        self.next_id = 1
        self.data = dict()
        
    def id(self, x):
        existing_id = self.data.get(x, None)

        if existing_id:
            return existing_id
            
        self.data[x] = self.next_id
        self.next_id += 1
        
        return self.next_id - 1



class NGramSpace(object):
    
    def __init__(self, n):
        self.n = n
        self.ngrams = Sequencer()
        
    def parse(self, text):
        split_text = text.lower().split()
        
        ids = set()
        
        for i in range(0, len(split_text) + 1 - self.n):
            ngram = " ".join(split_text[i:i+self.n])
            ids.add(self.ngrams.id(ngram))
            
        sorted_ids = list(ids)
        sorted_ids.sort()
        
        return sorted_ids
        

def overlap(x, y):
    i = 0
    j = 0
    
    c = 0
    
    while i < len(x) and j < len(y):
        if x[i] > y[j]:
            j += 1
        elif x[i] < y[j]:
            i += 1
        else: # x[i] == y[j]
            c += 1
            i += 1
            j += 1          
            
    return c
    

def jaccard(x, y):
    intersection_size = overlap(x, y)
    union_size = len(x) + len(y) - intersection_size
    
    return float(intersection_size) / union_size if union_size != 0 else 0

