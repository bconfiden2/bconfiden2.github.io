N = 6
M = 9

edges = """0 1 5
0 2 4
1 2 2
1 3 7
2 3 6
2 4 11
3 4 3
3 5 8
4 5 8"""

import heapq

parents = [i for i in range(N)]
def _find(x):
    if parents[x] == x: return x
    parents[x] = _find(parents[x])
    return parents[x]

pq = []
for line in edges.split('\n'):
    p, q, w = map(int, line.split())
    heapq.heappush(pq, (w, (p, q)))

cost = 0
while len(pq) > 0:
    c, (a, b) = heapq.heappop(pq)
    A, B = _find(a), _find(b)
    if A != B:
        cost += c
        parents[A] = B
print(cost)