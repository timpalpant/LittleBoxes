from networkx import Graph

from littleboxes.xword import XWFill

def build_conflict_graph(xword, possible_answers):
    '''Build a network describing non-conflicting answer choices

    Arguments:
        xword - a Crossword object
        possible_answers - a dictionary as returned from self.query_answers
            e.g. {XWClue: set(str)}

    Returns:
        NetworkX Graph where nodes are (XWClue, str) pairs with the string
        being a possible solution to the clue.  Edges connect nodes which
        could be played simultaneously without conflict (no self-edges).
    '''
    g = Graph()

    for xwclue, wordset in possible_answers.items():
        for word in wordset:
            if not xword.would_conflict(xwclue, word):
                g.add_node(XWFill(clue=xwclue, word=word))

    for n in g:
        testcopy = xword.copy()
        testcopy.set_fill(n.clue, n.word)

        for other_n in g:
            if n.clue.coord == other_n.clue.coord:
                continue

            if n.clue.coord.direction == other_n.clue.coord.direction:
                g.add_edge(n, other_n)
            elif not testcopy.would_conflict(other_n.clue, other_n.word):
                g.add_edge(n, other_n)

    return g
