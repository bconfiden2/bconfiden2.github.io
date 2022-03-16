import heapq

def dijkstra(start, graph, INF):
    distance = [INF for _ in range(len(graph))]
    pq = []
    distance[start] = 0
    heapq.heappush(pq, (0, start))

    while len(pq) > 0:
        cur_dist, cur_node = heapq.heappop(pq)
        cur_dist *= -1
        if cur_dist > distance[cur_node]:
            continue
        for next_node, next_dist in graph[cur_node]:
            if cur_dist + next_dist < distance[next_node]:
                distance[next_node] = cur_dist + next_dist
                heapq.heappush(pq, (-distance[next_node], next_node))
    return distance

graph = [
    [(1, 4), (7, 8)],
    [(0, 4), (7, 11), (2, 8)],
    [(1, 8), (8, 2), (5, 4), (3, 7)],
    [(2, 7), (5, 14), (4, 9)],
    [(3, 9), (5, 10)],
    [(2, 4), (6, 2), (3, 14), (4, 10)],
    [(7, 1), (8, 6), (5, 2)],
    [(0, 8), (1, 11), (8, 7), (6, 1)],
    [(2, 2), (7, 7), (6, 6)]
]

print(dijkstra(0, graph, 10**10))