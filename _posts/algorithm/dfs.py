N = 7

edges = """0 1
0 3
1 2
1 3
1 5
1 6
2 3
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

def dfs(graph, visited, cur):
    print(cur)
    visited[cur] = True
    for nxt in graph[cur]:
        if not visited[nxt]:
            dfs(graph, visited, nxt)
            
visited = [False for _ in range(N)]
for i in range(N):
    if not visited[i]:
        dfs(graph, visited, i)