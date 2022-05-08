N = 7

edges = """0 1
0 3
1 2
1 3
1 5
1 6
2 4
2 5
2 6
3 4
4 6"""

graph = [[] for _ in range(N)]
for line in edges.split('\n'):
    p, q = map(int, line.split())
    graph[p].append(q)
    graph[q].append(p)

def bfs(graph, start):
    visited = [False for _ in range(len(graph))]
    visited[start] = True
    width = [0 for _ in range(len(graph))]
    width[start] = 0

    q = [start]
    order = []
    cnt = 0
    while len(q) > 0:
        nq = []
        for cur in q:
            order.append(cur)
            width[cur] = cnt
            for nxt in graph[cur]:
                if not visited[nxt]:
                    visited[nxt] = True
                    nq.append(nxt)
        q = nq
        cnt += 1
    return width, order

print(bfs(graph, 0))