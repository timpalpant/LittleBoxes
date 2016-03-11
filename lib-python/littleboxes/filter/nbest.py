from Queue import PriorityQueue

def nbest(iterable, n, max_examined=None):
    q = PriorityQueue(n)
    for i, (p, sol) in enumerate(iterable):
        q.put((-p, sol))
        if max_examined and i >= max_examined:
            break

    result = []
    while not q.empty():
        result.append(q.get()[1])
    return result
