V = 9
input = """0 1
0 2
4 7
1 5
5 6
3 4
2 8"""

parents = [i for i in range(V)]

def _union(parents, x, y):
    x = _find(parents, x)
    y = _find(parents, y)
    if x != y:
        parents[x] = y

def _find(parents, x):
    if parents[x] == x:
        return x
    parents[x] = _find(parents, parents[x])
    return parents[x]

for line in input.split('\n'):
    p, q = map(int, line.split())
    _union(parents, p, q)

for i in range(V):
    print(_find(parents, i), end=" ")
print()