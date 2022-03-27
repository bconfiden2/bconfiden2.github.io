N = 6

weights = [5, 3, 2, 2, 4, 2]
edges = """0 1
0 3
1 2
2 4
2 5
3 4 
4 5"""

graph = [[] for _ in range(N)]
indegree = [0 for _ in range(N)]
for e in edges.split('\n'):
    p, q = map(int, e.split())
    graph[p].append(q)
    indegree[q] += 1

answer = []
q = [i for i,v in enumerate(indegree) if v==0]
while len(q) > 0:
    nq = []
    for cur in q:
        answer.append(cur)
        for nxt in graph[cur]:
            indegree[nxt] -= 1
            if indegree[nxt] == 0:
                nq.append(nxt)
    q = nq
print(answer)