from datetime import datetime
from django.conf import settings

def execute_file(cursor, filename):
    contents = " ".join([line for line in open(filename, 'r') if line[0:2] != '--'])
    statements = contents.split(';')[:-1] # split on semi-colon. Last element will be trailing whitespace

    for statement in statements:
        cursor.execute(statement)



def binary_search(a, x, key=None):
    """Given a sorted (decreasing) list, return the first element that is less than the target value."""
    
    left = 0
    right = len(a)
    
    while (left < right):
        mid = (right + left) / 2
        
        if (key(a[mid]) if key else a[mid]) >= x:
            left = mid + 1
        else:
            right = mid
    
    return right

def profile(f):
    def profiled_f(*args, **opts):
        print "Entering %s.%s" % (f.__module__, f.__name__)
        start = datetime.now()
        result = f(*args, **opts)
        print "Exiting %s.%s after %s" % (f.__module__, f.__name__, datetime.now() - start)
        return result
    
    if getattr(settings, 'ANALYSIS_PROFILE', False):
        return profiled_f
    
    return f
